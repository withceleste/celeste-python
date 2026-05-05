"""Tests for GenAI metric histogram emission."""

from collections.abc import AsyncIterator
from typing import Any, ClassVar

import pytest
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader

from celeste import telemetry
from celeste.io import Chunk, Output, Usage
from celeste.parameters import Parameters
from celeste.streaming import Stream


class _TestUsage(Usage):
    """Usage with input/output/cached/reasoning fields for metric tests."""

    input_tokens: int | None = None
    output_tokens: int | None = None
    cached_tokens: int | None = None
    reasoning_tokens: int | None = None


class _TestOutput(Output[str]):
    """Output for tests."""

    pass


class _TestStream(Stream[_TestOutput, Parameters, Chunk]):
    """Concrete Stream that aggregates usage from per-chunk metadata."""

    _usage_class: ClassVar[type[Usage]] = _TestUsage
    _chunk_class: ClassVar[type[Chunk]] = Chunk
    _output_class: ClassVar[type[Output]] = _TestOutput
    _empty_content: ClassVar[str] = ""

    def _aggregate_content(self, chunks: list[Chunk]) -> str:
        return "".join(chunk.content for chunk in chunks)

    def _parse_chunk(self, event: dict[str, Any]) -> Chunk | None:
        content = event.get("delta")
        if not content and "usage" not in event:
            return None
        usage = _TestUsage(**event["usage"]) if "usage" in event else None
        return Chunk(content=content or "", finish_reason=None, usage=usage)


async def _async_iter(events: list[dict[str, Any]]) -> AsyncIterator[dict[str, Any]]:
    for event in events:
        yield event


@pytest.fixture
def meter_setup(monkeypatch: pytest.MonkeyPatch) -> InMemoryMetricReader:
    """Wire fresh histograms backed by InMemoryMetricReader for assertions."""
    reader = InMemoryMetricReader()
    provider = MeterProvider(metric_readers=[reader])
    test_meter = provider.get_meter("celeste-test")
    monkeypatch.setattr(
        telemetry,
        "_token_usage_histogram",
        test_meter.create_histogram(
            name="gen_ai.client.token.usage",
            unit="{token}",
        ),
    )
    monkeypatch.setattr(
        telemetry,
        "_operation_duration_histogram",
        test_meter.create_histogram(
            name="gen_ai.client.operation.duration",
            unit="s",
        ),
    )
    return reader


def _collect_metric(reader: InMemoryMetricReader, name: str) -> list[Any]:
    """Pull metric data points by name from the reader."""
    metrics_data = reader.get_metrics_data()
    if metrics_data is None:
        return []
    points: list[Any] = []
    for resource_metric in metrics_data.resource_metrics:
        for scope_metric in resource_metric.scope_metrics:
            for metric in scope_metric.metrics:
                if metric.name == name:
                    points.extend(metric.data.data_points)
    return points


class TestRecordTokenUsage:
    """`record_token_usage` emits one record per token category."""

    def test_input_and_output_recorded_separately(
        self, meter_setup: InMemoryMetricReader
    ) -> None:
        """input + output usage produce two records with different `gen_ai.token.type`."""
        usage = _TestUsage(input_tokens=100, output_tokens=50)
        attrs = {"gen_ai.request.model": "test-model"}

        telemetry.record_token_usage(usage, attrs)

        points = _collect_metric(meter_setup, "gen_ai.client.token.usage")
        token_types = sorted(p.attributes["gen_ai.token.type"] for p in points)
        assert token_types == ["input", "output"]
        by_type = {p.attributes["gen_ai.token.type"]: p.sum for p in points}
        assert by_type["input"] == 100
        assert by_type["output"] == 50

    def test_cached_and_reasoning_recorded_with_dedicated_token_type(
        self, meter_setup: InMemoryMetricReader
    ) -> None:
        """cached_tokens and reasoning_tokens get distinct token.type values."""
        usage = _TestUsage(
            input_tokens=10, output_tokens=5, cached_tokens=8, reasoning_tokens=3
        )
        telemetry.record_token_usage(usage, {})

        points = _collect_metric(meter_setup, "gen_ai.client.token.usage")
        token_types = sorted(p.attributes["gen_ai.token.type"] for p in points)
        assert token_types == ["cached_input", "input", "output", "reasoning"]

    def test_none_fields_are_skipped(self, meter_setup: InMemoryMetricReader) -> None:
        """Fields set to None do not produce records."""
        usage = _TestUsage(input_tokens=10)
        telemetry.record_token_usage(usage, {})

        points = _collect_metric(meter_setup, "gen_ai.client.token.usage")
        assert len(points) == 1
        assert points[0].attributes["gen_ai.token.type"] == "input"


class TestRecordOperationDuration:
    """`record_operation_duration` records latency with optional error.type."""

    def test_success_records_duration_without_error_type(
        self, meter_setup: InMemoryMetricReader
    ) -> None:
        """Successful call: duration recorded, no error.type attribute."""
        telemetry.record_operation_duration(1.5, {"gen_ai.request.model": "test-model"})

        points = _collect_metric(meter_setup, "gen_ai.client.operation.duration")
        assert len(points) == 1
        assert "error.type" not in points[0].attributes
        assert points[0].sum == pytest.approx(1.5)

    def test_failure_records_duration_with_error_type(
        self, meter_setup: InMemoryMetricReader
    ) -> None:
        """Failed call: duration recorded with error.type set to exception class name."""
        telemetry.record_operation_duration(0.2, {}, error=ValueError("bad input"))

        points = _collect_metric(meter_setup, "gen_ai.client.operation.duration")
        assert len(points) == 1
        assert points[0].attributes["error.type"] == "ValueError"


class TestStreamingMetrics:
    """Streaming flows record duration covering full consumption."""

    async def test_streaming_records_duration_and_token_usage(
        self, meter_setup: InMemoryMetricReader
    ) -> None:
        """Natural exhaustion records both metrics with correct values."""
        events = [
            {"delta": "Hello"},
            {"delta": " world", "usage": {"input_tokens": 12, "output_tokens": 34}},
        ]
        stream = _TestStream(_async_iter(events))
        provider = (
            MeterProvider()
        )  # noop meter for span; the spans go to default tracer
        del provider
        span = telemetry.tracer.start_span("test")
        wrapped = telemetry.trace_stream(
            stream, span, metric_attributes={"gen_ai.request.model": "test-model"}
        )

        async for _ in wrapped:
            pass

        token_points = _collect_metric(meter_setup, "gen_ai.client.token.usage")
        duration_points = _collect_metric(
            meter_setup, "gen_ai.client.operation.duration"
        )
        assert len(token_points) == 2
        assert len(duration_points) == 1
        assert duration_points[0].sum > 0
        assert "error.type" not in duration_points[0].attributes
