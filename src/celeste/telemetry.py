"""OpenTelemetry GenAI telemetry for Celeste."""

import asyncio
import contextvars
import json
import os
import time
from collections.abc import AsyncIterator, Iterator
from contextlib import contextmanager, suppress
from types import TracebackType
from typing import Any

from anyio.from_thread import start_blocking_portal

from celeste.artifacts import Artifact
from celeste.core import Modality, Protocol, Provider, UsageField
from celeste.exceptions import StreamNotExhaustedError
from celeste.io import Input, Output, Usage
from celeste.models import Model
from celeste.streaming import Stream
from celeste.tools import ToolCall
from celeste.types import Message

_PROVIDER_NAME_MAP: dict[Provider, str] = {
    Provider.OPENAI: "openai",
    Provider.ANTHROPIC: "anthropic",
    Provider.GOOGLE: "gcp.gemini",
    Provider.MISTRAL: "mistral_ai",
    Provider.XAI: "x_ai",
    Provider.GROQ: "groq",
    Provider.DEEPSEEK: "deepseek",
    Provider.PERPLEXITY: "perplexity",
    Provider.COHERE: "cohere",
}

_MODALITY_OPERATION: dict[Modality, str] = {
    Modality.TEXT: "chat",
    Modality.EMBEDDINGS: "embeddings",
}


class _NoOpSpan:
    """Span stand-in used when ``opentelemetry-api`` is not installed."""

    def set_attribute(self, key: str, value: Any) -> None:
        """Discard the attribute."""

    def set_attributes(self, attributes: dict[str, Any]) -> None:
        """Discard the attribute mapping."""

    def set_status(self, *args: Any, **kwargs: Any) -> None:
        """Discard the status update."""

    def record_exception(self, *args: Any, **kwargs: Any) -> None:
        """Discard the exception."""

    def add_event(self, *args: Any, **kwargs: Any) -> None:
        """Discard the span event."""

    def end(self) -> None:
        """Discard the end signal."""


class _NoOpTracer:
    """Tracer stand-in used when ``opentelemetry-api`` is not installed."""

    @contextmanager
    def start_as_current_span(self, name: str, **kwargs: Any) -> Iterator[_NoOpSpan]:
        """Yield a no-op span as a context manager."""
        yield _NoOpSpan()

    def start_span(self, name: str, **kwargs: Any) -> _NoOpSpan:
        """Return a detached no-op span."""
        return _NoOpSpan()


@contextmanager
def _noop_use_span(span: Any, end_on_exit: bool = False) -> Iterator[Any]:
    """No-op stand-in for ``opentelemetry.trace.use_span``."""
    yield span


class _NoOpStatus:
    """Status stand-in used when ``opentelemetry-api`` is not installed."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Discard the status arguments."""


class _NoOpStatusCode:
    """StatusCode stand-in used when ``opentelemetry-api`` is not installed."""

    ERROR = "ERROR"


class _NoOpHistogram:
    """Histogram stand-in used when ``opentelemetry-api`` is not installed."""

    def record(self, value: float, attributes: dict[str, Any] | None = None) -> None:
        """Discard the metric record."""


class _NoOpMeter:
    """Meter stand-in used when ``opentelemetry-api`` is not installed."""

    def create_histogram(
        self, name: str, unit: str = "", description: str = ""
    ) -> _NoOpHistogram:
        """Return a no-op histogram."""
        return _NoOpHistogram()


try:
    from opentelemetry import metrics as _otel_metrics
    from opentelemetry import trace as _otel_trace
    from opentelemetry.trace import Status as _OtelStatus
    from opentelemetry.trace import StatusCode as _OtelStatusCode

    tracer: Any = _otel_trace.get_tracer("celeste")
    use_span: Any = _otel_trace.use_span
    Status: Any = _OtelStatus
    StatusCode: Any = _OtelStatusCode
    meter: Any = _otel_metrics.get_meter("celeste")
except ImportError:
    tracer = _NoOpTracer()
    use_span = _noop_use_span
    Status = _NoOpStatus
    StatusCode = _NoOpStatusCode
    meter = _NoOpMeter()


_token_usage_histogram: Any = meter.create_histogram(
    name="gen_ai.client.token.usage",
    unit="{token}",
    description="Tokens used per GenAI call, sliced by gen_ai.token.type.",
)
_operation_duration_histogram: Any = meter.create_histogram(
    name="gen_ai.client.operation.duration",
    unit="s",
    description="Wall-clock duration of GenAI calls.",
)


def request_attributes(
    *,
    model: Model,
    provider: Provider | None,
    protocol: Protocol | None,
    modality: Modality,
) -> dict[str, Any]:
    """Build GenAI request attributes for a span.

    Off-spec providers/modalities get ``celeste.*`` keys so the data is
    queryable without polluting the ``gen_ai.*`` namespace.

    Args:
        model: Resolved model.
        provider: Resolved provider, if any.
        protocol: Resolved protocol, if any.
        modality: Operation modality.

    Returns:
        Attribute dict suitable for passing to ``start_as_current_span``.
    """
    attrs: dict[str, Any] = {"gen_ai.request.model": model.id}
    provider_name = _PROVIDER_NAME_MAP.get(provider) if provider is not None else None
    if provider_name is not None:
        attrs["gen_ai.provider.name"] = provider_name
    elif protocol is not None:
        attrs["gen_ai.provider.name"] = protocol.value
    operation = _MODALITY_OPERATION.get(modality)
    if operation is not None:
        attrs["gen_ai.operation.name"] = operation
    else:
        attrs["celeste.modality"] = modality.value
    return attrs


def span_name(modality: Modality, model: Model) -> str:
    """Build the span name per GenAI semconv ``"{operation} {model}"``.

    Falls back to ``"celeste.{modality} {model}"`` for modalities the spec
    does not yet cover.
    """
    operation = _MODALITY_OPERATION.get(modality)
    if operation is not None:
        return f"{operation} {model.id}"
    return f"celeste.{modality.value} {model.id}"


# `Usage` field → semconv span attribute key. Off-spec fields use `celeste.usage.<field>`.
_GEN_AI_USAGE_FIELDS: dict[str, str] = {
    UsageField.INPUT_TOKENS: "gen_ai.usage.input_tokens",
    UsageField.OUTPUT_TOKENS: "gen_ai.usage.output_tokens",
    UsageField.TOTAL_TOKENS: "gen_ai.usage.total_tokens",
    UsageField.REASONING_TOKENS: "gen_ai.usage.reasoning_tokens",
    UsageField.CACHED_TOKENS: "gen_ai.usage.cached_input_tokens",
}

# `Usage` field → `gen_ai.token.type` metric dimension. `total_tokens` excluded to avoid double-count.
_GEN_AI_TOKEN_TYPES: dict[str, str] = {
    UsageField.INPUT_TOKENS: "input",
    UsageField.OUTPUT_TOKENS: "output",
    UsageField.REASONING_TOKENS: "reasoning",
    UsageField.CACHED_TOKENS: "cached_input",
}


def _iter_usage_numeric(usage: Usage) -> Iterator[tuple[str, int | float]]:
    """Yield (field_name, value) for each numeric `Usage` field that is set."""
    for field_name in type(usage).model_fields:
        value = getattr(usage, field_name, None)
        if isinstance(value, bool):
            continue
        if not isinstance(value, int | float):
            continue
        yield field_name, value


def output_attributes(output: Output[Any]) -> dict[str, Any]:
    """Extract GenAI response attributes from a typed Output."""
    attrs: dict[str, Any] = {}
    for field_name, value in _iter_usage_numeric(output.usage):
        semconv_key = _GEN_AI_USAGE_FIELDS.get(field_name)
        attrs[semconv_key or f"celeste.usage.{field_name}"] = value
    if output.finish_reason is not None and output.finish_reason.reason is not None:
        attrs["gen_ai.response.finish_reasons"] = (output.finish_reason.reason,)
    attrs["gen_ai.response.model"] = output.metadata["model"]
    return attrs


def record_token_usage(usage: Usage, attributes: dict[str, Any]) -> None:
    """Record one ``gen_ai.client.token.usage`` observation per token category."""
    for field_name, value in _iter_usage_numeric(usage):
        token_type = _GEN_AI_TOKEN_TYPES.get(field_name)
        if token_type is None:
            continue
        _token_usage_histogram.record(
            value,
            attributes={**attributes, "gen_ai.token.type": token_type},
        )


def record_operation_duration(
    duration_seconds: float,
    attributes: dict[str, Any],
    error: BaseException | None = None,
) -> None:
    """Record one ``gen_ai.client.operation.duration`` observation."""
    attrs = {**attributes}
    if error is not None:
        attrs["error.type"] = type(error).__name__
    _operation_duration_histogram.record(duration_seconds, attributes=attrs)


# Opt-in flag, read once at import (semconv-standard env name).
_CAPTURE_CONTENT: bool = (
    os.environ.get("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "")
    .strip()
    .lower()
    == "true"
)

# Maps celeste artifact classes to semconv part type names.
_ARTIFACT_PART_TYPES: dict[str, str] = {
    "ImageArtifact": "image",
    "AudioArtifact": "audio",
    "VideoArtifact": "video",
    "DocumentArtifact": "document",
}


def _artifact_part(artifact: Artifact) -> dict[str, Any]:
    """Convert a celeste artifact to a semconv part by URL reference."""
    part: dict[str, Any] = {
        "type": _ARTIFACT_PART_TYPES.get(type(artifact).__name__, "media"),
    }
    if artifact.url is not None:
        part["uri"] = artifact.url
    if artifact.mime_type is not None:
        part["mime_type"] = str(artifact.mime_type)
    return part


def _content_to_parts(content: Any) -> list[dict[str, Any]]:
    """Convert a celeste content value to a list of semconv parts."""
    if content is None:
        return []
    if isinstance(content, list):
        parts: list[dict[str, Any]] = []
        for item in content:
            parts.extend(_content_to_parts(item))
        return parts
    if isinstance(content, Artifact):
        return [_artifact_part(content)]
    if isinstance(content, str):
        return [{"type": "text", "content": content}]
    return [{"type": "text", "content": json.dumps(content, default=str)}]


def _tool_call_part(tool_call: ToolCall) -> dict[str, Any]:
    """Convert a ToolCall into a semconv tool_call part."""
    return {
        "type": "tool_call",
        "id": tool_call.id,
        "name": tool_call.name,
        "arguments": json.dumps(tool_call.arguments, default=str),
    }


def _message_to_dict(message: Message) -> dict[str, Any]:
    """Convert a celeste Message into a semconv ``{role, parts}`` dict."""
    parts = _content_to_parts(message.content)
    if message.reasoning is not None:
        parts.append({"type": "reasoning", "content": message.reasoning})
    if message.tool_calls:
        parts.extend(_tool_call_part(call) for call in message.tool_calls)
    return {"role": message.role.value, "parts": parts}


def _input_messages_event(inputs: Input) -> dict[str, Any] | None:
    """Build the ``gen_ai.input.messages`` event attributes, or None when capture is off."""
    if not _CAPTURE_CONTENT:
        return None
    messages: list[dict[str, Any]] = []
    for message in getattr(inputs, "messages", None) or []:
        if isinstance(message, Message):
            messages.append(_message_to_dict(message))
    prompt = getattr(inputs, "prompt", None)
    if prompt is not None:
        parts: list[dict[str, Any]] = [{"type": "text", "content": str(prompt)}]
        for media_field in ("image", "video", "audio", "document"):
            media = getattr(inputs, media_field, None)
            if media is not None:
                parts.extend(_content_to_parts(media))
        messages.append({"role": "user", "parts": parts})
    if not messages:
        return None
    return {"messages": json.dumps(messages, default=str)}


def _output_messages_event(output: Output[Any]) -> dict[str, Any] | None:
    """Build the ``gen_ai.output.messages`` event attributes, or None when capture is off."""
    if not _CAPTURE_CONTENT:
        return None
    parts = _content_to_parts(output.content)
    reasoning = getattr(output, "reasoning", None)
    if reasoning is not None:
        parts.append({"type": "reasoning", "content": reasoning})
    if output.tool_calls:
        parts.extend(_tool_call_part(call) for call in output.tool_calls)
    if not parts:
        return None
    return {
        "messages": json.dumps([{"role": "assistant", "parts": parts}], default=str)
    }


def add_input_event(span: Any, inputs: Input) -> None:
    """Add the ``gen_ai.input.messages`` event to ``span`` when capture is enabled."""
    event = _input_messages_event(inputs)
    if event is not None:
        span.add_event("gen_ai.input.messages", attributes=event)


def record_output(
    span: Any,
    output: Output[Any],
    metric_attributes: dict[str, Any],
) -> None:
    """Emit span attrs, content event, and token usage for a successful Output."""
    span.set_attributes(output_attributes(output))
    output_event = _output_messages_event(output)
    if output_event is not None:
        span.add_event("gen_ai.output.messages", attributes=output_event)
    record_token_usage(output.usage, metric_attributes)


@contextmanager
def gen_ai_span(
    *,
    model: Model,
    provider: Provider | None,
    protocol: Protocol | None,
    modality: Modality,
    extra_attributes: dict[str, Any] | None = None,
) -> Iterator[tuple[Any, dict[str, Any]]]:
    """Open a GenAI span and record operation duration on exit.

    Yields ``(span, request_attrs)``. On any exception, the duration is recorded
    with ``error.type`` set; on success it's recorded plain.
    """
    request_attrs = request_attributes(
        model=model, provider=provider, protocol=protocol, modality=modality
    )
    span_attrs = (
        {**request_attrs, **extra_attributes} if extra_attributes else request_attrs
    )
    started = time.monotonic()
    error: BaseException | None = None
    with tracer.start_as_current_span(
        span_name(modality, model), attributes=span_attrs
    ) as span:
        try:
            yield span, request_attrs
        except BaseException as exc:
            error = exc
            raise
        finally:
            record_operation_duration(
                time.monotonic() - started, request_attrs, error=error
            )


class _TracedStream:
    """Stream-shaped wrapper that emits GenAI telemetry against an OTel span."""

    def __init__(
        self,
        inner: Stream[Any, Any, Any],
        span: Any,
        metric_attributes: dict[str, Any] | None = None,
    ) -> None:
        """Initialize wrapper around a constructed Stream and a detached span."""
        self._inner = inner
        self._span = span
        self._metric_attributes = metric_attributes or {}
        self._started = time.monotonic()
        self._seen_first = False
        self._ended = False
        self._error: BaseException | None = None

    def __aiter__(self) -> "_TracedStream":
        """Return self as async iterator."""
        return self

    async def __anext__(self) -> Any:
        """Yield next chunk; emit TTFC on first, finalize span on terminal events."""
        try:
            chunk = await self._inner.__anext__()
        except (StopAsyncIteration, asyncio.CancelledError):
            self._finalize()
            raise
        except Exception as exc:
            self._error = exc
            self._span.record_exception(exc)
            self._span.set_status(Status(StatusCode.ERROR, str(exc)))
            self._finalize()
            raise
        if not self._seen_first:
            self._seen_first = True
            self._span.set_attribute(
                "gen_ai.response.time_to_first_chunk",
                time.monotonic() - self._started,
            )
        return chunk

    async def __aenter__(self) -> "_TracedStream":
        """Enter async context — return self for iteration."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        """Exit async context — close stream and finalize span."""
        await self.aclose()
        return False

    def __iter__(self) -> Iterator[Any]:
        """Sync iterator using a blocking portal — drives this wrapper's __anext__."""
        portal_cm = start_blocking_portal()
        portal = portal_cm.__enter__()
        try:
            while True:
                try:
                    yield portal.call(self.__anext__)
                except StopAsyncIteration:
                    return
        finally:
            if not self._ended:
                with suppress(RuntimeError):
                    portal.call(self.aclose)
            portal_cm.__exit__(None, None, None)

    def __enter__(self) -> "_TracedStream":
        """Enter sync context — delegate to inner Stream."""
        self._inner.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit sync context — delegate to inner Stream."""
        self._inner.__exit__(exc_type, exc_val, exc_tb)

    def __repr__(self) -> str:
        """Developer-friendly representation showing inner stream state."""
        return repr(self._inner)

    @property
    def output(self) -> Any:
        """Access final Output after stream exhaustion."""
        return self._inner.output

    async def aclose(self) -> None:
        """Close the inner stream and finalize the span."""
        await self._inner.aclose()
        self._finalize()

    def _finalize(self) -> None:
        """End the span exactly once; emit usage, metrics, and output event."""
        if self._ended:
            return
        self._ended = True
        record_operation_duration(
            time.monotonic() - self._started,
            self._metric_attributes,
            error=self._error,
        )
        try:
            output = self._inner.output
        except StreamNotExhaustedError:
            output = None
        if output is not None:
            record_output(self._span, output, self._metric_attributes)
        self._span.end()


def trace_stream(
    stream: Stream[Any, Any, Any],
    span: Any,
    metric_attributes: dict[str, Any] | None = None,
) -> _TracedStream:
    """Wrap a Stream to emit GenAI telemetry against ``span``."""
    return _TracedStream(stream, span, metric_attributes)


async def bind_first_pull_to_span(
    inner: AsyncIterator[dict[str, Any]],
    span: Any,
) -> AsyncIterator[dict[str, Any]]:
    """Run inner's first pull under a context where span is active; delegate the rest."""
    with use_span(span):
        ctx = contextvars.copy_context()

    async def _first() -> dict[str, Any]:
        return await inner.__anext__()

    task = asyncio.create_task(_first(), context=ctx)
    try:
        first = await task
    except StopAsyncIteration:
        return
    except BaseException:
        task.cancel()
        raise
    yield first
    async for event in inner:
        yield event


__all__ = [
    "Status",
    "StatusCode",
    "add_input_event",
    "bind_first_pull_to_span",
    "gen_ai_span",
    "meter",
    "output_attributes",
    "record_operation_duration",
    "record_output",
    "record_token_usage",
    "request_attributes",
    "span_name",
    "trace_stream",
    "tracer",
    "use_span",
]
