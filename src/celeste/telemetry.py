"""OpenTelemetry GenAI telemetry for Celeste."""

import asyncio
import time
from collections.abc import Iterator
from contextlib import contextmanager
from types import TracebackType
from typing import Any

from celeste.core import Modality, Protocol, Provider
from celeste.exceptions import StreamNotExhaustedError
from celeste.io import Output
from celeste.models import Model
from celeste.streaming import Stream

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


try:
    from opentelemetry import trace as _otel_trace
    from opentelemetry.trace import Status as _OtelStatus
    from opentelemetry.trace import StatusCode as _OtelStatusCode

    tracer: Any = _otel_trace.get_tracer("celeste")
    use_span: Any = _otel_trace.use_span
    Status: Any = _OtelStatus
    StatusCode: Any = _OtelStatusCode
except ImportError:
    tracer = _NoOpTracer()
    use_span = _noop_use_span
    Status = _NoOpStatus
    StatusCode = _NoOpStatusCode


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


def output_attributes(output: Output[Any]) -> dict[str, Any]:
    """Extract GenAI response attributes from a typed Output."""
    attrs: dict[str, Any] = {}
    input_tokens = getattr(output.usage, "input_tokens", None)
    output_tokens = getattr(output.usage, "output_tokens", None)
    if isinstance(input_tokens, int):
        attrs["gen_ai.usage.input_tokens"] = input_tokens
    if isinstance(output_tokens, int):
        attrs["gen_ai.usage.output_tokens"] = output_tokens
    if output.finish_reason is not None and output.finish_reason.reason is not None:
        attrs["gen_ai.response.finish_reasons"] = (output.finish_reason.reason,)
    return attrs


class _TracedStream:
    """Stream-shaped wrapper that emits GenAI telemetry against an OTel span."""

    def __init__(self, inner: Stream[Any, Any, Any], span: Any) -> None:
        """Initialize wrapper around a constructed Stream and a detached span."""
        self._inner = inner
        self._span = span
        self._started = time.monotonic()
        self._seen_first = False
        self._ended = False

    def __aiter__(self) -> "_TracedStream":
        """Return self as async iterator."""
        return self

    async def __anext__(self) -> Any:
        """Yield next chunk; emit TTFC on first, finalize span on terminal events."""
        with use_span(self._span, end_on_exit=False):
            try:
                chunk = await self._inner.__anext__()
            except (StopAsyncIteration, asyncio.CancelledError):
                self._finalize()
                raise
            except Exception as exc:
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
        """Delegate sync iteration to the inner Stream."""
        return iter(self._inner)

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
        """End the span exactly once; emit usage attrs if Output is populated."""
        if self._ended:
            return
        self._ended = True
        try:
            output = self._inner.output
        except StreamNotExhaustedError:
            output = None
        if output is not None:
            self._span.set_attributes(output_attributes(output))
        self._span.end()


def trace_stream(stream: Stream[Any, Any, Any], span: Any) -> _TracedStream:
    """Wrap a Stream to emit GenAI telemetry against ``span``."""
    return _TracedStream(stream, span)


__all__ = [
    "Status",
    "StatusCode",
    "output_attributes",
    "request_attributes",
    "span_name",
    "trace_stream",
    "tracer",
    "use_span",
]
