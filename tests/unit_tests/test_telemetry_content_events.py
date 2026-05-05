"""Tests for opt-in GenAI content events (`gen_ai.input.messages` / `output.messages`)."""

import json
from collections.abc import AsyncIterator
from typing import Any, ClassVar

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)
from opentelemetry.trace import Span

from celeste import telemetry
from celeste.artifacts import ImageArtifact
from celeste.io import Chunk, Output, Usage
from celeste.mime_types import ImageMimeType
from celeste.modalities.text.io import TextInput, TextOutput, TextUsage
from celeste.parameters import Parameters
from celeste.streaming import Stream
from celeste.tools import ToolCall
from celeste.types import Message, Role


@pytest.fixture
def capture_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Enable content capture by patching the module-level flag."""
    monkeypatch.setattr(telemetry, "_CAPTURE_CONTENT", True)


@pytest.fixture
def capture_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Force-disable content capture (default behavior)."""
    monkeypatch.setattr(telemetry, "_CAPTURE_CONTENT", False)


@pytest.fixture
def exporter() -> tuple[InMemorySpanExporter, TracerProvider]:
    """Wire an in-memory span exporter."""
    span_exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(span_exporter))
    return span_exporter, provider


def _start_span(provider: TracerProvider, name: str = "test") -> Span:
    """Start a detached span on the given provider's tracer."""
    return provider.get_tracer("celeste-test").start_span(name)


class _TestStreamUsage(Usage):
    """Usage with token fields for streaming tests."""

    input_tokens: int | None = None
    output_tokens: int | None = None


class _TestStreamOutput(Output[str]):
    """Output for streaming tests."""

    pass


class _TestStream(Stream[_TestStreamOutput, Parameters, Chunk]):
    """Concrete Stream that aggregates content + usage."""

    _usage_class: ClassVar[type[Usage]] = _TestStreamUsage
    _chunk_class: ClassVar[type[Chunk]] = Chunk
    _output_class: ClassVar[type[Output]] = _TestStreamOutput
    _empty_content: ClassVar[str] = ""

    def _aggregate_content(self, chunks: list[Chunk]) -> str:
        return "".join(chunk.content for chunk in chunks)

    def _parse_chunk(self, event: dict[str, Any]) -> Chunk | None:
        content = event.get("delta")
        if not content and "usage" not in event:
            return None
        usage = _TestStreamUsage(**event["usage"]) if "usage" in event else None
        return Chunk(content=content or "", finish_reason=None, usage=usage)


async def _async_iter(events: list[dict[str, Any]]) -> AsyncIterator[dict[str, Any]]:
    for event in events:
        yield event


class TestInputMessagesEvent:
    """`_input_messages_event` builds the input messages payload from typed inputs."""

    def test_capture_disabled_returns_none(self, capture_disabled: None) -> None:
        """With the env flag off, the helper returns None — no event emitted."""
        inputs = TextInput(prompt="hello")
        assert telemetry._input_messages_event(inputs) is None

    def test_text_prompt_only(self, capture_enabled: None) -> None:
        """Plain text prompt produces a single user message with one text part."""
        inputs = TextInput(prompt="hello")

        result = telemetry._input_messages_event(inputs)

        assert result is not None
        messages = json.loads(result["messages"])
        assert messages == [
            {"role": "user", "parts": [{"type": "text", "content": "hello"}]}
        ]

    def test_messages_field_emitted(self, capture_enabled: None) -> None:
        """When `inputs.messages` is set, those messages are serialized verbatim."""
        inputs = TextInput(
            messages=[
                Message(role=Role.SYSTEM, content="be helpful"),
                Message(role=Role.USER, content="hi"),
            ]
        )

        result = telemetry._input_messages_event(inputs)

        assert result is not None
        messages = json.loads(result["messages"])
        assert messages[0]["role"] == "system"
        assert messages[0]["parts"] == [{"type": "text", "content": "be helpful"}]
        assert messages[1]["role"] == "user"

    def test_image_input_emitted_as_reference(self, capture_enabled: None) -> None:
        """Images attached to a prompt are emitted as URL references, not bytes."""
        inputs = TextInput(
            prompt="describe this",
            image=ImageArtifact(
                url="https://example.com/img.png",
                mime_type=ImageMimeType.PNG,
            ),
        )

        result = telemetry._input_messages_event(inputs)

        assert result is not None
        messages = json.loads(result["messages"])
        parts = messages[0]["parts"]
        assert parts[0]["type"] == "text"
        image_parts = [p for p in parts if p["type"] == "image"]
        assert len(image_parts) == 1
        assert image_parts[0]["uri"] == "https://example.com/img.png"
        assert image_parts[0]["mime_type"] == "image/png"


class TestOutputMessagesEvent:
    """`_output_messages_event` builds the assistant payload from a typed Output."""

    def test_capture_disabled_returns_none(self, capture_disabled: None) -> None:
        """With the env flag off, the helper returns None."""
        output = TextOutput(content="reply", usage=TextUsage())
        assert telemetry._output_messages_event(output) is None

    def test_text_only(self, capture_enabled: None) -> None:
        """Plain text output produces a single assistant message with one text part."""
        output = TextOutput(content="reply", usage=TextUsage())

        result = telemetry._output_messages_event(output)

        assert result is not None
        messages = json.loads(result["messages"])
        assert messages == [
            {"role": "assistant", "parts": [{"type": "text", "content": "reply"}]}
        ]

    def test_reasoning_appended(self, capture_enabled: None) -> None:
        """Reasoning content is appended as a `reasoning` part."""
        output = TextOutput(
            content="answer", usage=TextUsage(), reasoning="thinking..."
        )

        result = telemetry._output_messages_event(output)

        assert result is not None
        parts = json.loads(result["messages"])[0]["parts"]
        types = [p["type"] for p in parts]
        assert "text" in types and "reasoning" in types
        reasoning_part = next(p for p in parts if p["type"] == "reasoning")
        assert reasoning_part["content"] == "thinking..."

    def test_tool_calls_emitted_as_tool_call_parts(self, capture_enabled: None) -> None:
        """Tool calls become semconv `tool_call` parts with id/name/arguments."""
        output = TextOutput(
            content="",
            usage=TextUsage(),
            tool_calls=[
                ToolCall(id="call_1", name="get_weather", arguments={"city": "Paris"})
            ],
        )

        result = telemetry._output_messages_event(output)

        assert result is not None
        parts = json.loads(result["messages"])[0]["parts"]
        tool_parts = [p for p in parts if p["type"] == "tool_call"]
        assert len(tool_parts) == 1
        assert tool_parts[0]["id"] == "call_1"
        assert tool_parts[0]["name"] == "get_weather"
        assert json.loads(tool_parts[0]["arguments"]) == {"city": "Paris"}

    def test_image_artifact_output_by_reference(self, capture_enabled: None) -> None:
        """Image generation outputs emit URL references, never inline bytes."""
        output = TextOutput(
            content=ImageArtifact(
                url="https://example.com/out.png", mime_type=ImageMimeType.PNG
            ),
            usage=TextUsage(),
        )

        result = telemetry._output_messages_event(output)

        assert result is not None
        parts = json.loads(result["messages"])[0]["parts"]
        assert parts[0]["type"] == "image"
        assert parts[0]["uri"] == "https://example.com/out.png"
        assert parts[0]["mime_type"] == "image/png"


class TestStreamingContentEvents:
    """Streaming flows emit content events at finalize when output is built."""

    async def test_natural_exhaustion_emits_output_event(
        self,
        capture_enabled: None,
        exporter: tuple[InMemorySpanExporter, TracerProvider],
    ) -> None:
        """After exhaustion, the span carries the `gen_ai.output.messages` event."""
        in_memory, provider = exporter
        events = [
            {"delta": "Hello"},
            {"delta": " world", "usage": {"input_tokens": 1, "output_tokens": 2}},
        ]
        stream = _TestStream(_async_iter(events))
        span = _start_span(provider)
        wrapped = telemetry.trace_stream(stream, span)

        async for _ in wrapped:
            pass

        finished = in_memory.get_finished_spans()
        assert len(finished) == 1
        event_names = [e.name for e in finished[0].events]
        assert "gen_ai.output.messages" in event_names

    async def test_aclose_before_output_skips_output_event(
        self,
        capture_enabled: None,
        exporter: tuple[InMemorySpanExporter, TracerProvider],
    ) -> None:
        """When _output is None at finalize, the output event is skipped."""
        in_memory, provider = exporter
        events = [{"delta": "Partial"}, {"delta": "..."}]
        stream = _TestStream(_async_iter(events))
        span = _start_span(provider)
        wrapped = telemetry.trace_stream(stream, span)

        await wrapped.__anext__()
        await wrapped.aclose()

        finished = in_memory.get_finished_spans()
        assert len(finished) == 1
        event_names = [e.name for e in finished[0].events]
        assert "gen_ai.output.messages" not in event_names
