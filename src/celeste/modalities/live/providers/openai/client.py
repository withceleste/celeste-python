"""OpenAI live client."""

from typing import Any

from celeste.artifacts import AudioArtifact
from celeste.messages import content_to_text, message_parts, require_part
from celeste.mime_types import AudioMimeType
from celeste.parameters import ParameterMapper
from celeste.protocols.openresponses.tools import parse_tool_calls
from celeste.providers.openai.live import config
from celeste.providers.openai.live.client import OpenAILiveClient as OpenAILiveMixin
from celeste.providers.openai.live.streaming import (
    OpenAILiveStream as _OpenAILiveStream,
)
from celeste.tools import ToolCall, ToolResult
from celeste.types import Message, Role, TextPart

from ...client import LiveClient
from ...io import LiveChunk, LiveInput
from ...streaming import LiveStream
from .parameters import OPENAI_PARAMETER_MAPPERS


class OpenAILiveStream(_OpenAILiveStream, LiveStream):
    """OpenAI streaming for live modality."""

    def _parse_chunk_transcript(self, event_data: dict[str, Any]) -> Message | None:
        """Build a transcript fragment from input or output transcript deltas."""
        role = {
            "session.input_transcript.delta": Role.USER,
            "session.output_transcript.delta": Role.ASSISTANT,
        }.get(event_data.get("type", ""))
        if role is None or not event_data.get("delta"):
            return None
        return Message(role=role, content=event_data["delta"])

    def _parse_chunk_tool_calls(self, event_data: dict[str, Any]) -> list[ToolCall]:
        """Build function calls completed by the delegated Responses backend."""
        inner = event_data.get("event", {})
        if (
            event_data.get("type") != "response.event"
            or inner.get("type") != "response.output_item.done"
        ):
            return []
        return [
            call.model_copy(update={"delegation_id": event_data.get("delegation_id")})
            for call in parse_tool_calls({"output": [inner.get("item", {})]})
        ]

    def _serialize_tool_result(self, result: ToolResult) -> list[dict[str, Any]]:
        """Append a result; the application explicitly resumes backend work."""
        return [
            {
                "type": "response.item.create",
                "item": {
                    "type": "function_call_output",
                    "call_id": result.tool_call_id,
                    "output": content_to_text(result.content),
                },
            }
        ]

    def _serialize_audio(self, audio: AudioArtifact) -> list[dict[str, Any]]:
        """Append raw bytes matching the startup audio format."""
        return [{"type": "session.input_audio.append", "audio": audio.get_base64()}]

    def _aggregate_content(self, chunks: list[LiveChunk]) -> AudioArtifact:
        """Aggregate audio bytes into AudioArtifact in the format session.started confirmed."""
        started: dict[str, Any] = next(
            (
                chunk.metadata["event_data"]
                for chunk in chunks
                if chunk.metadata["event_data"].get("type") == "session.started"
            ),
            {},
        )
        audio_format = (
            started.get("session", {})
            .get("audio", {})
            .get("format", config.DEFAULT_AUDIO_FORMAT)
        )
        return AudioArtifact(
            data=b"".join(chunk.content for chunk in chunks),
            mime_type=AudioMimeType(audio_format["type"]),
            metadata={"sample_rate": audio_format["rate"]},
        )


class OpenAILiveClient(OpenAILiveMixin, LiveClient):
    """OpenAI live client."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[AudioArtifact]]:
        return OPENAI_PARAMETER_MAPPERS

    def _init_request(self, inputs: LiveInput) -> dict[str, Any]:
        """Seed text history, preserving developer roles and system instructions."""
        instructions = []
        history = []
        for message in inputs.messages or []:
            if isinstance(message, ToolResult) or message.tool_calls:
                msg = "OpenAI Live startup history accepts text messages only"
                raise ValueError(msg)
            parts = message_parts(message.content)
            for part in parts:
                require_part("OpenAI Live", part, (TextPart,))
            text = "".join(part.text for part in parts if isinstance(part, TextPart))
            if message.role == Role.SYSTEM:
                instructions.append(text)
            elif message.role in (Role.USER, Role.ASSISTANT, Role.DEVELOPER):
                history.append(
                    {
                        "type": "message",
                        "role": message.role.value,
                        "content": [
                            {
                                "type": "output_text"
                                if message.role == Role.ASSISTANT
                                else "input_text",
                                "text": text,
                            }
                        ],
                    }
                )
            else:
                msg = f"Unsupported OpenAI Live history role: {message.role}"
                raise ValueError(msg)
        request: dict[str, Any] = {}
        if instructions:
            request["instructions"] = "\n".join(instructions)
        if history:
            request["input"] = history
        return request

    def _stream_class(self) -> type[LiveStream]:
        """Return the Stream class for this provider."""
        return OpenAILiveStream


__all__ = ["OpenAILiveClient", "OpenAILiveStream"]
