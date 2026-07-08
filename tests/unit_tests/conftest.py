"""Shared pytest fixtures for unit tests."""

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)
from opentelemetry.trace import Span
from pydantic import SecretStr

from celeste import Model
from celeste.auth import AuthHeader
from celeste.constraints import Constraint
from celeste.core import Modality, Operation, Provider
from celeste.modalities.text.providers.anthropic.client import AnthropicTextClient


def anthropic_test_client(
    constraints: dict[str, Constraint] | None = None,
) -> AnthropicTextClient:
    """Anthropic text client over a minimal model, for request/stream tests."""
    model = Model(
        id="claude-opus-4-8",
        provider=Provider.ANTHROPIC,
        display_name="Claude Opus 4.8",
        operations={Modality.TEXT: {Operation.GENERATE}},
        parameter_constraints=constraints or {},
    )
    return AnthropicTextClient(
        model=model,
        provider=Provider.ANTHROPIC,
        auth=AuthHeader(secret=SecretStr("test"), header="x-api-key", prefix=""),
    )


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
