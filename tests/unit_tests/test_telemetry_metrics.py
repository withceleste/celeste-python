"""Tests for GenAI metric histogram emission."""

from typing import Any

import pytest
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader

from celeste import telemetry
from tests.unit_tests._telemetry_helpers import (
    TelemetryStream,
    TelemetryUsage,
    async_iter,
)


@pytest.fixture
def meter_setup(monkeypatch: pytest.MonkeyPatch) -> InMemoryMetricReader:
    """Wire fresh histograms backed by InMemoryMetricReader for assertions."""
    reader = InMemoryMetricReader()
    test_meter = MeterProvider(metric_readers=[reader]).get_meter("celeste-test")
    monkeypatch.setattr(
        telemetry,
        "_token_usage_histogram",
        test_meter.create_histogram(name="gen_ai.client.token.usage", unit="{token}"),
    )
    monkeypatch.setattr(
        telemetry,
        "_operation_duration_histogram",
        test_meter.create_histogram(name="gen_ai.client.operation.duration", unit="s"),
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


@pytest.mark.parametrize(
    ("usage_kwargs", "expected_token_types", "expected_sums"),
    [
        (
            {
                "input_tokens": 10,
                "output_tokens": 5,
                "cached_tokens": 8,
                "reasoning_tokens": 3,
            },
            ["cached_input", "input", "output", "reasoning"],
            {"input": 10, "output": 5, "cached_input": 8, "reasoning": 3},
        ),
        (
            {"input_tokens": 100, "output_tokens": 50},
            ["input", "output"],
            {"input": 100, "output": 50},
        ),
        ({"input_tokens": 10}, ["input"], {"input": 10}),
    ],
    ids=["all_token_types", "input_output_only", "input_only_others_none"],
)
def test_record_token_usage_emits_one_record_per_category(
    meter_setup: InMemoryMetricReader,
    usage_kwargs: dict[str, int],
    expected_token_types: list[str],
    expected_sums: dict[str, int],
) -> None:
    """Each populated token field produces one record with a distinct token.type."""
    telemetry.record_token_usage(TelemetryUsage(**usage_kwargs), {})

    points = _collect_metric(meter_setup, "gen_ai.client.token.usage")
    assert (
        sorted(p.attributes["gen_ai.token.type"] for p in points)
        == expected_token_types
    )
    assert {p.attributes["gen_ai.token.type"]: p.sum for p in points} == expected_sums


@pytest.mark.parametrize(
    ("error", "expected_error_type"),
    [(None, None), (ValueError("bad input"), "ValueError")],
    ids=["success", "failure"],
)
def test_record_operation_duration_with_optional_error_type(
    meter_setup: InMemoryMetricReader,
    error: BaseException | None,
    expected_error_type: str | None,
) -> None:
    """Duration is recorded; error.type appears on failure only."""
    telemetry.record_operation_duration(1.5, {"gen_ai.request.model": "m"}, error=error)

    points = _collect_metric(meter_setup, "gen_ai.client.operation.duration")
    assert len(points) == 1
    assert points[0].sum == pytest.approx(1.5)
    assert points[0].attributes.get("error.type") == expected_error_type


async def test_streaming_records_duration_and_token_usage(
    meter_setup: InMemoryMetricReader,
) -> None:
    """Natural exhaustion records both metrics with correct values."""
    events = [
        {"delta": "Hello"},
        {"delta": " world", "usage": {"input_tokens": 12, "output_tokens": 34}},
    ]
    span = telemetry.tracer.start_span("test")
    wrapped = telemetry.trace_stream(
        TelemetryStream(async_iter(events)),
        span,
        metric_attributes={"gen_ai.request.model": "test-model"},
    )

    async for _ in wrapped:
        pass

    token_points = _collect_metric(meter_setup, "gen_ai.client.token.usage")
    duration_points = _collect_metric(meter_setup, "gen_ai.client.operation.duration")
    assert len(token_points) == 2
    assert len(duration_points) == 1
    assert duration_points[0].sum >= 0
    assert "error.type" not in duration_points[0].attributes
