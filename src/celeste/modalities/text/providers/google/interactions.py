"""Google text client (Interactions API — default path for API-key auth)."""

from typing import Any

from celeste.grounding import Grounding
from celeste.messages import content_to_text, message_parts, request_messages
from celeste.parameters import ParameterMapper
from celeste.providers.google.interactions.client import (
    GoogleInteractionsClient as GoogleInteractionsMixin,
)
from celeste.providers.google.interactions.streaming import (
    GoogleInteractionsStream as _GoogleInteractionsStream,
)
from celeste.providers.google.interactions.streaming import reconstruct_steps
from celeste.providers.google.interactions.tools import tool_calls_from_steps
from celeste.providers.google.utils import build_content_part
from celeste.tools import ToolCall, ToolResult
from celeste.types import (
    AudioPart,
    DocumentPart,
    ImagePart,
    MessageContent,
    Role,
    TextContent,
    TextPart,
    VideoPart,
)

from ...client import TextClient
from ...io import TextInput
from ...streaming import TextStream
from .grounding import map_grounding_interactions
from .parameters import GOOGLE_INTERACTIONS_PARAMETER_MAPPERS


class GoogleInteractionsTextStream(_GoogleInteractionsStream, TextStream):
    """Google streaming for text modality (Interactions API)."""

    _step_events: list[dict[str, Any]]

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        super().__init__(*args, **kwargs)
        self._step_events = []

    def _parse_chunk(self, event: dict[str, Any]) -> Any:  # noqa: ANN401
        """Retain step lifecycle events that base chunk filtering would drop."""
        event_type = event.get("event_type") or ""
        if event_type.startswith("step.") or event_type == "interaction.completed":
            self._step_events.append(event)
        return super()._parse_chunk(event)

    def _aggregate_event_data(self, chunks: list[Any]) -> list[dict[str, Any]]:
        """Return the retained step events (chunk metadata lacks step.start/stop)."""
        return self._step_events

    def _aggregate_grounding(
        self, chunks: list, raw_events: list[dict[str, Any]]
    ) -> Grounding | None:
        """Aggregate grounding from the reconstructed steps."""
        return map_grounding_interactions(reconstruct_steps(raw_events))

    def _aggregate_tool_calls(
        self, chunks: list, raw_events: list[dict[str, Any]]
    ) -> list[ToolCall]:
        """Extract tool calls from the reconstructed steps."""
        return tool_calls_from_steps(reconstruct_steps(raw_events))

    def _aggregate_signature(
        self, chunks: list, raw_events: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Extract thought steps (for signature continuity) from reconstructed steps."""
        return [
            step
            for step in reconstruct_steps(raw_events)
            if step.get("type") == "thought"
        ]


class GoogleInteractionsTextClient(GoogleInteractionsMixin, TextClient):
    """Google text client (Interactions API)."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return GOOGLE_INTERACTIONS_PARAMETER_MAPPERS

    def _init_request(self, inputs: TextInput) -> dict[str, Any]:
        """Initialize request from Google Interactions input-turns format."""

        def content_to_parts(content: MessageContent) -> list[dict[str, Any]]:
            """Convert message content to an Interactions API content-parts array."""
            parts: list[dict[str, Any]] = []
            for part in message_parts(content):
                if isinstance(part, TextPart):
                    if part.text:
                        parts.append({"type": "text", "text": part.text})
                elif isinstance(part, ImagePart):
                    parts.append(build_content_part(part.image, "image"))
                elif isinstance(part, VideoPart):
                    parts.append(build_content_part(part.video, "video"))
                elif isinstance(part, AudioPart):
                    parts.append(build_content_part(part.audio, "audio"))
                elif isinstance(part, DocumentPart):
                    parts.append(build_content_part(part.document, "document"))
            return parts

        system_texts: list[str] = []
        turns: list[dict[str, Any]] = []

        for msg in request_messages(
            prompt=inputs.prompt,
            messages=inputs.messages,
            image=inputs.image,
            video=inputs.video,
            audio=inputs.audio,
            document=inputs.document,
        ):
            if msg.role in {Role.SYSTEM, Role.DEVELOPER}:
                for part in message_parts(msg.content):
                    if isinstance(part, TextPart):
                        system_texts.append(part.text)
                continue

            if isinstance(msg, ToolResult):
                turns.append(
                    {
                        "type": "function_result",
                        "name": msg.name,
                        "call_id": msg.tool_call_id,
                        "result": [
                            {"type": "text", "text": content_to_text(msg.content)}
                        ],
                    }
                )
                continue

            turn_type = "model_output" if msg.role == Role.ASSISTANT else "user_input"
            for sig_block in msg.signature or []:
                turns.append(sig_block)
            content_parts = content_to_parts(msg.content)
            if content_parts:
                turns.append({"type": turn_type, "content": content_parts})
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    turn: dict[str, Any] = {
                        "type": "function_call",
                        "id": tc.id,
                        "name": tc.name,
                        "arguments": tc.arguments,
                    }
                    signature = getattr(tc, "signature", None)
                    if signature:
                        turn["signature"] = signature
                    turns.append(turn)

        result: dict[str, Any] = {"input": turns}
        if system_texts:
            result["system_instruction"] = "\n\n".join(system_texts)
        return result

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> TextContent:
        """Parse text across all model_output steps (matches stream concatenation)."""
        steps = super()._parse_content(response_data)
        texts = [
            part.get("text")
            for step in steps
            if step.get("type") == "model_output"
            for part in step.get("content", [])
            if part.get("type") == "text" and part.get("text") is not None
        ]
        return "".join(texts)

    def _parse_reasoning(
        self, response_data: dict[str, Any]
    ) -> tuple[str | None, list[dict[str, Any]]]:
        """Parse thought steps from Google response."""
        steps = response_data.get("steps", [])
        reasoning_parts: list[str] = []
        signature_blocks: list[dict[str, Any]] = []
        for step in steps:
            if step.get("type") != "thought":
                continue
            signature_blocks.append(step)
            for part in step.get("summary", []) or []:
                if part.get("type") == "text" and part.get("text"):
                    reasoning_parts.append(part["text"])
        text = "\n".join(reasoning_parts) if reasoning_parts else None
        return text, signature_blocks

    def _parse_grounding(self, response_data: dict[str, Any]) -> Grounding | None:
        """Extract Google grounding from google_search steps and text annotations."""
        return map_grounding_interactions(response_data.get("steps", []))

    def _parse_tool_calls(self, response_data: dict[str, Any]) -> list[ToolCall]:
        """Parse tool calls from Google response."""
        return tool_calls_from_steps(response_data.get("steps", []))

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return GoogleInteractionsTextStream


__all__ = ["GoogleInteractionsTextClient", "GoogleInteractionsTextStream"]
