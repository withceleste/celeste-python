"""Tests for opt-in GenAI content events (`gen_ai.input.messages` / `output.messages`)."""

import json

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

from celeste import telemetry
from celeste.artifacts import ImageArtifact
from celeste.mime_types import ImageMimeType
from celeste.modalities.text.io import TextInput, TextOutput, TextUsage
from celeste.tools import ToolCall
from celeste.types import Message, Role
from tests.unit_tests._telemetry_helpers import TelemetryStream, async_iter
from tests.unit_tests.conftest import start_test_span


@pytest.fixture
def capture_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Enable content capture by patching the module-level flag."""
    monkeypatch.setattr(telemetry, "_CAPTURE_CONTENT", True)


@pytest.fixture
def capture_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Force-disable content capture (default behavior)."""
    monkeypatch.setattr(telemetry, "_CAPTURE_CONTENT", False)


class TestInputMessagesEvent:
    def test_capture_disabled_returns_none(self, capture_disabled: None) -> None:
        """With the env flag off, the helper returns None — no event emitted."""
        assert telemetry._input_messages_event(TextInput(prompt="hello")) is None

    def test_text_prompt_only(self, capture_enabled: None) -> None:
        """Plain text prompt produces a single user message with one text part."""
        result = telemetry._input_messages_event(TextInput(prompt="hello"))

        assert result is not None
        assert json.loads(result["messages"]) == [
            {"role": "user", "parts": [{"type": "text", "content": "hello"}]}
        ]

    def test_messages_field_emitted(self, capture_enabled: None) -> None:
        """When `inputs.messages` is set, those messages are serialized verbatim."""
        result = telemetry._input_messages_event(
            TextInput(
                messages=[
                    Message(role=Role.SYSTEM, content="be helpful"),
                    Message(role=Role.USER, content="hi"),
                ]
            )
        )

        assert result is not None
        messages = json.loads(result["messages"])
        assert messages[0]["role"] == "system"
        assert messages[0]["parts"] == [{"type": "text", "content": "be helpful"}]
        assert messages[1]["role"] == "user"

    def test_image_input_emitted_as_reference(self, capture_enabled: None) -> None:
        """Images attached to a prompt are emitted as URL references, not bytes."""
        result = telemetry._input_messages_event(
            TextInput(
                prompt="describe this",
                image=ImageArtifact(
                    url="https://example.com/img.png", mime_type=ImageMimeType.PNG
                ),
            )
        )

        assert result is not None
        parts = json.loads(result["messages"])[0]["parts"]
        assert parts[0]["type"] == "text"
        image_parts = [p for p in parts if p["type"] == "image"]
        assert len(image_parts) == 1
        assert image_parts[0]["uri"] == "https://example.com/img.png"
        assert image_parts[0]["mime_type"] == "image/png"


class TestOutputMessagesEvent:
    def test_capture_disabled_returns_none(self, capture_disabled: None) -> None:
        """With the env flag off, the helper returns None."""
        assert (
            telemetry._output_messages_event(
                TextOutput(content="reply", usage=TextUsage())
            )
            is None
        )

    def test_text_only(self, capture_enabled: None) -> None:
        """Plain text output produces a single assistant message with one text part."""
        result = telemetry._output_messages_event(
            TextOutput(content="reply", usage=TextUsage())
        )

        assert result is not None
        assert json.loads(result["messages"]) == [
            {"role": "assistant", "parts": [{"type": "text", "content": "reply"}]}
        ]

    def test_reasoning_appended(self, capture_enabled: None) -> None:
        """Reasoning content is appended as a `reasoning` part."""
        result = telemetry._output_messages_event(
            TextOutput(content="answer", usage=TextUsage(), reasoning="thinking...")
        )

        assert result is not None
        parts = json.loads(result["messages"])[0]["parts"]
        assert {p["type"] for p in parts} == {"text", "reasoning"}
        assert (
            next(p for p in parts if p["type"] == "reasoning")["content"]
            == "thinking..."
        )

    def test_tool_calls_emitted_as_tool_call_parts(self, capture_enabled: None) -> None:
        """Tool calls become semconv `tool_call` parts with id/name/arguments."""
        result = telemetry._output_messages_event(
            TextOutput(
                content="",
                usage=TextUsage(),
                tool_calls=[
                    ToolCall(
                        id="call_1", name="get_weather", arguments={"city": "Paris"}
                    )
                ],
            )
        )

        assert result is not None
        tool_parts = [
            p
            for p in json.loads(result["messages"])[0]["parts"]
            if p["type"] == "tool_call"
        ]
        assert len(tool_parts) == 1
        assert tool_parts[0]["id"] == "call_1"
        assert tool_parts[0]["name"] == "get_weather"
        assert json.loads(tool_parts[0]["arguments"]) == {"city": "Paris"}

    def test_image_artifact_output_by_reference(self, capture_enabled: None) -> None:
        """Image generation outputs emit URL references, never inline bytes."""
        result = telemetry._output_messages_event(
            TextOutput(
                content=ImageArtifact(
                    url="https://example.com/out.png", mime_type=ImageMimeType.PNG
                ),
                usage=TextUsage(),
            )
        )

        assert result is not None
        parts = json.loads(result["messages"])[0]["parts"]
        assert parts[0] == {
            "type": "image",
            "uri": "https://example.com/out.png",
            "mime_type": "image/png",
        }


class TestStreamingContentEvents:
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
        wrapped = telemetry.trace_stream(
            TelemetryStream(async_iter(events)), start_test_span(provider)
        )

        async for _ in wrapped:
            pass

        finished = in_memory.get_finished_spans()
        assert len(finished) == 1
        assert "gen_ai.output.messages" in [e.name for e in finished[0].events]

    async def test_aclose_before_output_skips_output_event(
        self,
        capture_enabled: None,
        exporter: tuple[InMemorySpanExporter, TracerProvider],
    ) -> None:
        """When _output is None at finalize, the output event is skipped."""
        in_memory, provider = exporter
        wrapped = telemetry.trace_stream(
            TelemetryStream(async_iter([{"delta": "Partial"}, {"delta": "..."}])),
            start_test_span(provider),
        )

        await wrapped.__anext__()
        await wrapped.aclose()

        finished = in_memory.get_finished_spans()
        assert len(finished) == 1
        assert "gen_ai.output.messages" not in [e.name for e in finished[0].events]
