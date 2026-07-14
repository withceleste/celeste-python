"""Tests for `_TracedStream` — span lifecycle and GenAI attribute emission."""

import asyncio
from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import patch

import pytest
from opentelemetry import trace as otel_trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)
from opentelemetry.trace import StatusCode

from celeste import telemetry
from celeste.exceptions import StreamNotExhaustedError
from celeste.io import Output, Usage
from tests.unit_tests._telemetry_helpers import (
    TelemetryOutput,
    TelemetryStream,
    TelemetryUsage,
    async_iter,
)
from tests.unit_tests.conftest import start_test_span


class _OffSpecUsage(Usage):
    """Modality-specific usage with fields outside the GenAI semconv set."""

    images_generated: int | None = None
    audio_seconds: float | None = None


async def _failing_iter() -> AsyncIterator[dict[str, Any]]:
    """Async iterator that raises before yielding any event."""
    raise RuntimeError("boom")
    yield  # pragma: no cover — needed to mark this as an async generator


class TestNaturalExhaustion:
    async def test_emits_input_output_tokens_on_natural_exhaustion(
        self, exporter: tuple[InMemorySpanExporter, TracerProvider]
    ) -> None:
        """After `async for` to completion, span carries gen_ai.usage.*_tokens."""
        in_memory, provider = exporter
        events = [
            {"delta": "Hello"},
            {"delta": " world", "usage": {"input_tokens": 12, "output_tokens": 34}},
        ]
        wrapped = telemetry.trace_stream(
            TelemetryStream(async_iter(events)), start_test_span(provider)
        )

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
        events = [{"delta": "Hi", "usage": {"input_tokens": 1, "output_tokens": 2}}]
        wrapped = telemetry.trace_stream(
            TelemetryStream(async_iter(events)), start_test_span(provider)
        )

        async with wrapped as ctx:
            async for _ in ctx:
                pass

        finished = in_memory.get_finished_spans()
        assert len(finished) == 1
        attrs = finished[0].attributes or {}
        assert attrs["gen_ai.usage.input_tokens"] == 1
        assert attrs["gen_ai.usage.output_tokens"] == 2


class TestEarlyAbandonment:
    async def test_aclose_before_output_built_emits_no_usage(
        self, exporter: tuple[InMemorySpanExporter, TracerProvider]
    ) -> None:
        """When _output is None at aclose time, span ends without usage attrs."""
        in_memory, provider = exporter
        events = [{"delta": "Partial"}, {"delta": " result"}]
        wrapped = telemetry.trace_stream(
            TelemetryStream(async_iter(events)), start_test_span(provider)
        )

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
    async def test_exception_records_and_sets_error_status(
        self, exporter: tuple[InMemorySpanExporter, TracerProvider]
    ) -> None:
        """Exception during iteration sets ERROR status, ends span, propagates."""
        in_memory, provider = exporter
        wrapped = telemetry.trace_stream(
            TelemetryStream(_failing_iter()), start_test_span(provider)
        )

        with pytest.raises(RuntimeError, match="boom"):
            async for _ in wrapped:
                pass

        finished = in_memory.get_finished_spans()
        assert len(finished) == 1
        assert finished[0].status.status_code == StatusCode.ERROR
        assert any(e.name == "exception" for e in finished[0].events)


class TestPublicSurface:
    async def test_output_raises_before_exhaustion(
        self, exporter: tuple[InMemorySpanExporter, TracerProvider]
    ) -> None:
        """Accessing .output mid-stream raises StreamNotExhaustedError."""
        _, provider = exporter
        wrapped = telemetry.trace_stream(
            TelemetryStream(async_iter([{"delta": "x"}])), start_test_span(provider)
        )

        with pytest.raises(StreamNotExhaustedError):
            _ = wrapped.output

    async def test_output_returns_typed_output_after_exhaustion(
        self, exporter: tuple[InMemorySpanExporter, TracerProvider]
    ) -> None:
        """After exhaustion, .output returns the typed Output from inner."""
        _, provider = exporter
        events = [{"delta": "abc", "usage": {"input_tokens": 1, "output_tokens": 1}}]
        wrapped = telemetry.trace_stream(
            TelemetryStream(async_iter(events)), start_test_span(provider)
        )

        async for _ in wrapped:
            pass

        output = wrapped.output
        assert isinstance(output, TelemetryOutput)
        assert output.content == "abc"
        assert output.usage.input_tokens == 1


class TestIdempotentFinalize:
    async def test_natural_exhaustion_then_aclose_ends_span_once(
        self, exporter: tuple[InMemorySpanExporter, TracerProvider]
    ) -> None:
        """`async for` to completion then `aclose()` produces a single span."""
        in_memory, provider = exporter
        events = [{"delta": "x", "usage": {"input_tokens": 2, "output_tokens": 3}}]
        wrapped = telemetry.trace_stream(
            TelemetryStream(async_iter(events)), start_test_span(provider)
        )

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
        wrapped = telemetry.trace_stream(
            TelemetryStream(async_iter(events)), start_test_span(provider)
        )

        async for _ in wrapped:
            pass

        attrs = in_memory.get_finished_spans()[0].attributes or {}
        assert attrs["gen_ai.usage.input_tokens"] == 10
        assert attrs["gen_ai.usage.output_tokens"] == 5
        assert attrs["gen_ai.usage.total_tokens"] == 15
        assert attrs["gen_ai.usage.reasoning_tokens"] == 3
        assert attrs["gen_ai.usage.cached_input_tokens"] == 8

    def test_off_spec_usage_emitted_under_celeste_namespace(self) -> None:
        """Modality-specific Usage fields fall through to `celeste.usage.<field>`."""
        usage = _OffSpecUsage(images_generated=4, audio_seconds=1.5)
        output: Output[Any] = TelemetryOutput(
            content="", usage=usage, metadata={"model": "test-model"}
        )

        attrs = telemetry.output_attributes(output)

        assert attrs["celeste.usage.images_generated"] == 4
        assert attrs["celeste.usage.audio_seconds"] == 1.5
        assert "gen_ai.usage.images_generated" not in attrs

    def test_response_model_emitted_from_metadata(self) -> None:
        output: Output[Any] = TelemetryOutput(
            content="",
            usage=TelemetryUsage(),
            metadata={"response_model": "claude-opus-4-1-20250805"},
        )

        attrs = telemetry.output_attributes(output)

        assert attrs["gen_ai.response.model"] == "claude-opus-4-1-20250805"

    def test_response_model_omitted_when_provider_does_not_return_one(self) -> None:
        output: Output[Any] = TelemetryOutput(
            content="", usage=TelemetryUsage(), metadata={}
        )

        assert "gen_ai.response.model" not in telemetry.output_attributes(output)


class TestNoSpanActivationInAnext:
    """Regression: `_TracedStream.__anext__` must not activate the span across `await`."""

    async def test_anext_does_not_call_use_span(
        self, exporter: tuple[InMemorySpanExporter, TracerProvider]
    ) -> None:
        """Iterating a `_TracedStream` does NOT invoke `telemetry.use_span`."""
        _, provider = exporter
        events = [{"delta": "a"}, {"delta": "b"}]
        wrapped = telemetry.trace_stream(
            TelemetryStream(async_iter(events)), start_test_span(provider)
        )

        with patch("celeste.telemetry.use_span") as mock_use_span:
            async for _ in wrapped:
                pass

        mock_use_span.assert_not_called()


class TestBindFirstPullToSpan:
    """`bind_first_pull_to_span` runs the first pull with span active; delegates the rest."""

    async def test_preserves_event_order(
        self, exporter: tuple[InMemorySpanExporter, TracerProvider]
    ) -> None:
        """All events from inner are yielded in original order."""
        _, provider = exporter
        events = [{"i": 0}, {"i": 1}, {"i": 2}]
        bound = telemetry.bind_first_pull_to_span(
            async_iter(events), start_test_span(provider)
        )

        collected = [event async for event in bound]

        assert collected == events

    async def test_empty_stream_yields_nothing(
        self, exporter: tuple[InMemorySpanExporter, TracerProvider]
    ) -> None:
        """Inner that immediately raises StopAsyncIteration yields no events."""
        _, provider = exporter
        bound = telemetry.bind_first_pull_to_span(
            async_iter([]), start_test_span(provider)
        )

        collected = [event async for event in bound]

        assert collected == []

    async def test_first_error_propagates(
        self, exporter: tuple[InMemorySpanExporter, TracerProvider]
    ) -> None:
        """Exception raised by inner's first pull propagates to the consumer."""
        _, provider = exporter
        bound = telemetry.bind_first_pull_to_span(
            _failing_iter(), start_test_span(provider)
        )

        with pytest.raises(RuntimeError, match="boom"):
            async for _ in bound:
                pass

    async def test_first_pull_runs_with_span_active(
        self, exporter: tuple[InMemorySpanExporter, TracerProvider]
    ) -> None:
        """First inner pull sees span as current OTel context; subsequent pulls don't."""
        _, provider = exporter
        span = start_test_span(provider)
        target_id = span.get_span_context().span_id

        async def inner() -> AsyncIterator[dict[str, int]]:
            yield {"span_id": otel_trace.get_current_span().get_span_context().span_id}
            yield {"span_id": otel_trace.get_current_span().get_span_context().span_id}

        bound = telemetry.bind_first_pull_to_span(inner(), span)
        collected = [event async for event in bound]

        assert collected[0]["span_id"] == target_id
        assert collected[1]["span_id"] != target_id

    async def test_cancel_during_first_pull_cancels_inner_task(
        self, exporter: tuple[InMemorySpanExporter, TracerProvider]
    ) -> None:
        """Cancellation while awaiting the first pull propagates to the inner task — no leak."""
        _, provider = exporter
        started = asyncio.Event()

        async def slow_inner() -> AsyncIterator[dict[str, str]]:
            started.set()
            await asyncio.sleep(60)
            yield {"v": "never"}

        bound = telemetry.bind_first_pull_to_span(
            slow_inner(), start_test_span(provider)
        )
        consumer: asyncio.Task[dict[str, str]] = asyncio.create_task(bound.__anext__())
        await started.wait()
        consumer.cancel()
        with pytest.raises(asyncio.CancelledError):
            await consumer
        await asyncio.sleep(0)
