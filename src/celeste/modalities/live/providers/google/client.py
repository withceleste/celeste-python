"""Google live client."""

from typing import Any

from celeste.artifacts import AudioArtifact, ImageArtifact
from celeste.messages import message_parts, require_part, tool_result_object
from celeste.mime_types import AudioMimeType, ImageMimeType
from celeste.parameters import ParameterMapper
from celeste.providers.google.generate_content.tools import (
    needs_native_replay,
    tool_calls_from_parts,
)
from celeste.providers.google.live.client import GoogleLiveClient as GoogleLiveMixin
from celeste.providers.google.live.streaming import (
    GoogleLiveStream as _GoogleLiveStream,
)
from celeste.providers.google.utils import build_media_part
from celeste.tools import ToolCall, ToolResult
from celeste.types import AudioPart, ImagePart, Message, Role, TextPart, VideoPart
from celeste.utils.mime import split_sample_rate

from ...client import LiveClient
from ...io import LiveChunk, LiveInput, LiveUsage
from ...streaming import LiveStream
from .parameters import GOOGLE_PARAMETER_MAPPERS


def build_content(message: Message | ToolResult) -> dict[str, Any]:
    """Serialize canonical message parts, tool calls, and tool results."""
    if isinstance(message, ToolResult):
        return {
            "role": "user",
            "parts": [
                {
                    "functionResponse": {
                        "id": message.tool_call_id,
                        "name": message.name,
                        "response": {"result": tool_result_object(message)},
                    }
                }
            ],
        }
    if message.signature and needs_native_replay(message.signature):
        return {"role": "model", "parts": message.signature}
    parts = list(message.signature or [])
    for part in message_parts(message.content):
        require_part("Google Live", part, (TextPart, ImagePart, AudioPart, VideoPart))
        if isinstance(part, TextPart):
            parts.append({"text": part.text})
        elif isinstance(part, ImagePart):
            parts.append(build_media_part(part.image))
        elif isinstance(part, AudioPart):
            parts.append(build_media_part(part.audio))
        elif isinstance(part, VideoPart):
            parts.append(build_media_part(part.video))
    for call in message.tool_calls or []:
        parts.append(
            {"functionCall": {"id": call.id, "name": call.name, "args": call.arguments}}
        )
    return {
        "role": "model" if message.role == Role.ASSISTANT else "user",
        "parts": parts,
    }


class GoogleLiveStream(_GoogleLiveStream, LiveStream):
    """Google streaming for live modality."""

    def _parse_chunk_transcript(self, event_data: dict[str, Any]) -> Message | None:
        """Build a transcript fragment from input or output transcription."""
        content = event_data.get("serverContent", {})
        for key, role in (
            ("inputTranscription", Role.USER),
            ("outputTranscription", Role.ASSISTANT),
        ):
            text = content.get(key, {}).get("text")
            if text:
                return Message(role=role, content=text)
        return None

    def _parse_chunk_tool_calls(self, event_data: dict[str, Any]) -> list[ToolCall]:
        """Build tool calls from a toolCall event."""
        return tool_calls_from_parts(
            [
                {"functionCall": call}
                for call in event_data.get("toolCall", {}).get("functionCalls", [])
            ]
        )

    def _serialize_message(self, message: Message) -> list[dict[str, Any]]:
        """Send user input or assistant context as ordered client content."""
        if message.role not in (Role.USER, Role.ASSISTANT):
            msg = "Google Live system instructions belong in session setup"
            raise ValueError(msg)
        return [
            {
                "clientContent": {
                    "turns": [build_content(message)],
                    "turnComplete": message.role == Role.USER,
                }
            }
        ]

    def _serialize_tool_result(self, result: ToolResult) -> list[dict[str, Any]]:
        """Deliver the application's function result."""
        return [
            {
                "toolResponse": {
                    "functionResponses": [
                        {
                            "id": result.tool_call_id,
                            "name": result.name,
                            "response": {"result": tool_result_object(result)},
                        }
                    ]
                }
            }
        ]

    def _serialize_audio(self, audio: AudioArtifact) -> list[dict[str, Any]]:
        """Send the declared raw audio format without transcoding."""
        mime = audio.mime_type or AudioMimeType.PCM
        if mime == AudioMimeType.PCM:
            mime = (
                f"{AudioMimeType.PCM};rate={audio.metadata.get('sample_rate', 16000)}"
            )
        return [
            {"realtimeInput": {"audio": {"data": audio.get_base64(), "mimeType": mime}}}
        ]

    def _serialize_image(self, image: ImageArtifact) -> list[dict[str, Any]]:
        """Send one frame; capture rate belongs to the application."""
        return [
            {
                "realtimeInput": {
                    "video": {
                        "data": image.get_base64(),
                        "mimeType": image.mime_type or ImageMimeType.JPEG,
                    }
                }
            }
        ]

    def _aggregate_usage(self, chunks: list[LiveChunk]) -> LiveUsage:
        """Sum the last usage snapshot of each model turn; Live reports usage per turn."""
        total: dict[str, int | float] = {}
        current: LiveUsage | None = None
        for chunk in chunks:
            current = chunk.usage or current
            turn_complete = (
                chunk.metadata["event_data"]
                .get("serverContent", {})
                .get("turnComplete")
            )
            if current is not None and (turn_complete or chunk is chunks[-1]):
                for key, value in current.model_dump(exclude_none=True).items():
                    total[key] = total.get(key, 0) + value
                current = None
        return LiveUsage(**total)

    def _aggregate_content(self, chunks: list[LiveChunk]) -> AudioArtifact:
        """Aggregate audio bytes from chunks into AudioArtifact."""
        mime, rate = split_sample_rate(self._audio_mime_type or AudioMimeType.PCM)
        return AudioArtifact(
            data=b"".join(chunk.content for chunk in chunks),
            mime_type=AudioMimeType(mime),
            metadata={"sample_rate": rate} if rate else {},
        )


class GoogleLiveClient(GoogleLiveMixin, LiveClient):
    """Google live client."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[AudioArtifact]]:
        return GOOGLE_PARAMETER_MAPPERS

    def _init_request(self, inputs: LiveInput) -> dict[str, Any]:
        """Initialize setup with audio output, transcription, and seeded history."""
        system_parts: list[dict[str, Any]] = []
        turns: list[dict[str, Any]] = []
        for message in inputs.messages or []:
            content = build_content(message)
            if message.role in (Role.SYSTEM, Role.DEVELOPER):
                system_parts.extend(content["parts"])
            else:
                turns.append(content)
        request: dict[str, Any] = {
            "generationConfig": {"responseModalities": ["AUDIO"]},
            "inputAudioTranscription": {},
            "outputAudioTranscription": {},
            "clientContent": {"turns": turns, "turnComplete": False},
        }
        if system_parts:
            request["systemInstruction"] = {"parts": system_parts}
        return request

    def _stream_class(self) -> type[LiveStream]:
        """Return the Stream class for this provider."""
        return GoogleLiveStream


__all__ = ["GoogleLiveClient", "GoogleLiveStream"]
