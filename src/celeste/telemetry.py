"""OpenTelemetry GenAI telemetry for Celeste."""

import time
from collections.abc import AsyncIterator, Iterator
from contextlib import contextmanager
from typing import Any

from celeste.core import Modality, Protocol, Provider
from celeste.io import Output
from celeste.models import Model

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


try:
    from opentelemetry import trace as _otel_trace

    tracer: Any = _otel_trace.get_tracer("celeste")
    use_span: Any = _otel_trace.use_span
except ImportError:
    tracer = _NoOpTracer()
    use_span = _noop_use_span


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


async def trace_stream(
    sse_iterator: AsyncIterator[dict[str, Any]],
    span: Any,
) -> AsyncIterator[dict[str, Any]]:
    """Wrap an SSE iterator to record TTFC and end the span at iteration's end.

    OTel's ``use_span(span, end_on_exit=True)`` context manager makes the
    span current, auto-records exceptions, sets ERROR status on exception,
    and ends the span on exit (including ``GeneratorExit`` from consumer
    abandonment). No try/except needed.
    """
    with use_span(span, end_on_exit=True):
        started = time.monotonic()
        seen_first = False
        async for event in sse_iterator:
            if not seen_first:
                seen_first = True
                span.set_attribute(
                    "gen_ai.response.time_to_first_chunk",
                    time.monotonic() - started,
                )
            yield event


__all__ = [
    "output_attributes",
    "request_attributes",
    "span_name",
    "trace_stream",
    "tracer",
    "use_span",
]
