"""Tests for `_TracedStream` — span lifecycle and GenAI attribute emission."""

from collections.abc import AsyncIterator
from typing import Any, ClassVar

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)
from opentelemetry.trace import Span, StatusCode

from celeste import telemetry
from celeste.exceptions import StreamNotExhaustedError
from celeste.io import Chunk, Output, Usage
from celeste.parameters import Parameters
from celeste.streaming import Stream


class _TestUsage(Usage):
    """Usage with the full GenAI semconv field set for telemetry assertions."""

    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    reasoning_tokens: int | None = None
    cached_tokens: int | None = None


class _OffSpecUsage(Usage):
    """Modality-specific usage with fields outside the GenAI semconv set."""

    images_generated: int | None = None
    audio_seconds: float | None = None


class _TestOutput(Output[str]):
    """Output for tests."""

    pass


class _TestStream(Stream[_TestOutput, Parameters, Chunk]):
    """Stream that aggregates usage from per-chunk metadata for tests."""

    _usage_class: ClassVar[type[Usage]] = _TestUsage
    _chunk_class: ClassVar[type[Chunk]] = Chunk
    _output_class: ClassVar[type[Output]] = _TestOutput
    _empty_content: ClassVar[str] = ""

    def _aggregate_content(self, chunks: list[Chunk]) -> str:
        """Concatenate chunk content."""
        return "".join(chunk.content for chunk in chunks)

    def _parse_chunk(self, event: dict[str, Any]) -> Chunk | None:
        """Parse delta events; lifecycle events return None."""
        content = event.get("delta")
        if not content and "usage" not in event:
            return None
        usage = _TestUsage(**event["usage"]) if "usage" in event else None
        return Chunk(content=content or "", finish_reason=None, usage=usage)


async def _async_iter(events: list[dict[str, Any]]) -> AsyncIterator[dict[str, Any]]:
    """Convert a list of events into an async iterator."""
    for event in events:
        yield event


async def _failing_iter() -> AsyncIterator[dict[str, Any]]:
    """Async iterator that raises before yielding any event."""
    raise RuntimeError("boom")
    yield  # pragma: no cover — needed to mark this as an async generator


@pytest.fixture
def exporter() -> tuple[InMemorySpanExporter, TracerProvider]:
    """In-memory span exporter wired into a fresh TracerProvider."""
    span_exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(span_exporter))
    return span_exporter, provider


def _start_span(provider: TracerProvider, name: str = "test") -> Span:
    """Start a detached span on the given provider's tracer."""
    return provider.get_tracer("celeste-test").start_span(name)


class TestNaturalExhaustion:
    """Span emits usage attrs from inner._output after natural exhaustion."""

    async def test_emits_input_output_tokens_on_natural_exhaustion(
        self, exporter: tuple[InMemorySpanExporter, TracerProvider]
    ) -> None:
        """After `async for` to completion, span carries gen_ai.usage.*_tokens."""
        in_memory, provider = exporter
        events = [
            {"delta": "Hello"},
            {"delta": " world", "usage": {"input_tokens": 12, "output_tokens": 34}},
        ]
        stream = _TestStream(_async_iter(events))
        span = _start_span(provider)
        wrapped = telemetry.trace_stream(stream, span)

        chunks = [chunk async for chunk in wrapped]

        assert len(chunks) == 2
        finished = in_memory.get_finished_spans()
        assert len(finished) == 1
        attrs = finished[0].attributes or {}
        assert attrs["gen_ai.usage.input_tokens"] == 12
        assert attrs["gen_ai.usage.output_tokens"] == 34
        assert "gen_ai.response.time_to_first_chunk" in attrs

    async def test_async_context_manager_emits_usage(
        self, exporter: tuple[InMemorySpanExporter, TracerProvider]
    ) -> None:
        """`async with wrapped: async for ...` emits usage and ends the span once."""
        in_memory, provider = exporter
        events = [
            {"delta": "Hi", "usage": {"input_tokens": 1, "output_tokens": 2}},
        ]
        stream = _TestStream(_async_iter(events))
        span = _start_span(provider)
        wrapped = telemetry.trace_stream(stream, span)

        async with wrapped as ctx:
            async for _ in ctx:
                pass

        finished = in_memory.get_finished_spans()
        assert len(finished) == 1
        attrs = finished[0].attributes or {}
        assert attrs["gen_ai.usage.input_tokens"] == 1
        assert attrs["gen_ai.usage.output_tokens"] == 2


class TestEarlyAbandonment:
    """`aclose()` before exhaustion ends the span without usage attrs."""

    async def test_aclose_before_output_built_emits_no_usage(
        self, exporter: tuple[InMemorySpanExporter, TracerProvider]
    ) -> None:
        """When _output is None at aclose time, span ends without usage attrs."""
        in_memory, provider = exporter
        events = [
            {"delta": "Partial"},
            {"delta": " result"},
        ]
        stream = _TestStream(_async_iter(events))
        span = _start_span(provider)
        wrapped = telemetry.trace_stream(stream, span)

        chunk = await wrapped.__anext__()
        assert chunk.content == "Partial"
        await wrapped.aclose()

        finished = in_memory.get_finished_spans()
        assert len(finished) == 1
        attrs = finished[0].attributes or {}
        assert "gen_ai.usage.input_tokens" not in attrs
        assert "gen_ai.usage.output_tokens" not in attrs
        assert finished[0].status.status_code != StatusCode.ERROR


class TestExceptionPath:
    """Exceptions during iteration are recorded with ERROR status."""

    async def test_exception_records_and_sets_error_status(
        self, exporter: tuple[InMemorySpanExporter, TracerProvider]
    ) -> None:
        """Exception during iteration sets ERROR status, ends span, propagates."""
        in_memory, provider = exporter
        stream = _TestStream(_failing_iter())
        span = _start_span(provider)
        wrapped = telemetry.trace_stream(stream, span)

        with pytest.raises(RuntimeError, match="boom"):
            async for _ in wrapped:
                pass

        finished = in_memory.get_finished_spans()
        assert len(finished) == 1
        assert finished[0].status.status_code == StatusCode.ERROR
        events = list(finished[0].events)
        assert any(e.name == "exception" for e in events)


class TestPublicSurface:
    """Wrapper preserves the public Stream surface used by consumers."""

    async def test_output_raises_before_exhaustion(
        self, exporter: tuple[InMemorySpanExporter, TracerProvider]
    ) -> None:
        """Accessing .output mid-stream raises StreamNotExhaustedError."""
        _, provider = exporter
        stream = _TestStream(_async_iter([{"delta": "x"}]))
        span = _start_span(provider)
        wrapped = telemetry.trace_stream(stream, span)

        with pytest.raises(StreamNotExhaustedError):
            _ = wrapped.output

    async def test_output_returns_typed_output_after_exhaustion(
        self, exporter: tuple[InMemorySpanExporter, TracerProvider]
    ) -> None:
        """After exhaustion, .output returns the typed Output from inner."""
        _, provider = exporter
        events = [{"delta": "abc", "usage": {"input_tokens": 1, "output_tokens": 1}}]
        stream = _TestStream(_async_iter(events))
        span = _start_span(provider)
        wrapped = telemetry.trace_stream(stream, span)

        async for _ in wrapped:
            pass

        output = wrapped.output
        assert isinstance(output, _TestOutput)
        assert output.content == "abc"
        assert output.usage.input_tokens == 1


class TestIdempotentFinalize:
    """Span ends exactly once across natural exhaustion and explicit aclose."""

    async def test_natural_exhaustion_then_aclose_ends_span_once(
        self, exporter: tuple[InMemorySpanExporter, TracerProvider]
    ) -> None:
        """`async for` to completion then `aclose()` produces a single span."""
        in_memory, provider = exporter
        events = [{"delta": "x", "usage": {"input_tokens": 2, "output_tokens": 3}}]
        stream = _TestStream(_async_iter(events))
        span = _start_span(provider)
        wrapped = telemetry.trace_stream(stream, span)

        async for _ in wrapped:
            pass
        await wrapped.aclose()

        finished = in_memory.get_finished_spans()
        assert len(finished) == 1
        attrs = finished[0].attributes or {}
        assert attrs["gen_ai.usage.input_tokens"] == 2
        assert attrs["gen_ai.usage.output_tokens"] == 3


class TestExtendedUsageAttributes:
    """V2 widens `output_attributes` to emit total/reasoning/cached_input tokens."""

    async def test_total_reasoning_cached_tokens_emitted(
        self, exporter: tuple[InMemorySpanExporter, TracerProvider]
    ) -> None:
        """When the typed Usage carries the full set, all attributes appear on the span."""
        in_memory, provider = exporter
        events = [
            {
                "delta": "ok",
                "usage": {
                    "input_tokens": 10,
                    "output_tokens": 5,
                    "total_tokens": 15,
                    "reasoning_tokens": 3,
                    "cached_tokens": 8,
                },
            }
        ]
        stream = _TestStream(_async_iter(events))
        span = _start_span(provider)
        wrapped = telemetry.trace_stream(stream, span)

        async for _ in wrapped:
            pass

        finished = in_memory.get_finished_spans()
        attrs = finished[0].attributes or {}
        assert attrs["gen_ai.usage.input_tokens"] == 10
        assert attrs["gen_ai.usage.output_tokens"] == 5
        assert attrs["gen_ai.usage.total_tokens"] == 15
        assert attrs["gen_ai.usage.reasoning_tokens"] == 3
        assert attrs["gen_ai.usage.cached_input_tokens"] == 8

    def test_off_spec_usage_emitted_under_celeste_namespace(self) -> None:
        """Modality-specific Usage fields fall through to `celeste.usage.<field>`."""
        usage = _OffSpecUsage(images_generated=4, audio_seconds=1.5)
        output = _TestOutput(content="", usage=usage)

        attrs = telemetry.output_attributes(output)

        assert attrs["celeste.usage.images_generated"] == 4
        assert attrs["celeste.usage.audio_seconds"] == 1.5
        assert "gen_ai.usage.images_generated" not in attrs
