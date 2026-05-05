"""Shared pytest fixtures for unit tests."""

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)
from opentelemetry.trace import Span


@pytest.fixture
def exporter() -> tuple[InMemorySpanExporter, TracerProvider]:
    """In-memory span exporter wired into a fresh TracerProvider."""
    span_exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(span_exporter))
    return span_exporter, provider


def start_test_span(provider: TracerProvider, name: str = "test") -> Span:
    """Start a detached span on the given provider's tracer."""
    return provider.get_tracer("celeste-test").start_span(name)
