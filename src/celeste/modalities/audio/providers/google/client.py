"""Google audio client (Interactions API)."""

import base64
from typing import Any

from celeste.artifacts import AudioArtifact
from celeste.mime_types import AudioMimeType
from celeste.parameters import ParameterMapper
from celeste.providers.google.interactions import config
from celeste.providers.google.interactions.client import (
    GoogleInteractionsClient as GoogleInteractionsMixin,
)
from celeste.providers.google.interactions.streaming import (
    GoogleInteractionsStream as _GoogleInteractionsStream,
)
from celeste.types import AudioContent

from ...client import AudioClient
from ...io import AudioChunk, AudioInput
from ...streaming import AudioStream
from .parameters import GOOGLE_PARAMETER_MAPPERS, OutputFormatMapper

# Interactions audio mime strings → celeste audio mime types
GOOGLE_AUDIO_MIME_TYPES: dict[str, AudioMimeType] = {
    wire: mime for mime, wire in OutputFormatMapper.mime_map.items()
} | {"audio/mpeg": AudioMimeType.MP3}


def _to_audio_mime(raw: str | None) -> AudioMimeType:
    """Translate an Interactions audio mime string (default audio/l16 PCM)."""
    codec = (raw or "").split(";")[0].strip()
    return GOOGLE_AUDIO_MIME_TYPES.get(codec, AudioMimeType.PCM)


class GoogleAudioStream(_GoogleInteractionsStream, AudioStream):
    """Google streaming for audio modality (Interactions API)."""

    _audio_meta: dict[str, Any]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._audio_meta = {}

    def _parse_chunk_content(self, event_data: dict[str, Any]) -> bytes | None:
        """Extract audio bytes from a step.delta event."""
        if event_data.get("event_type") != "step.delta":
            return None
        delta = event_data.get("delta", {})
        if delta.get("type") != "audio" or not delta.get("data"):
            return None
        if not self._audio_meta:
            self._audio_meta = {
                "mime_type": delta.get("mime_type"),
                "sample_rate": delta.get("sample_rate"),
                "channels": delta.get("channels"),
            }
        return base64.b64decode(delta["data"])

    def _aggregate_content(self, chunks: list[AudioChunk]) -> AudioArtifact:
        """Aggregate audio bytes from chunks into AudioArtifact."""
        audio_bytes = b"".join(chunk.content for chunk in chunks if chunk.content)
        meta = self._audio_meta
        return AudioArtifact(
            data=audio_bytes,
            mime_type=_to_audio_mime(meta.get("mime_type")),
            metadata={k: meta[k] for k in ("sample_rate", "channels") if meta.get(k)},
        )


class GoogleAudioClient(GoogleInteractionsMixin, AudioClient):
    """Google audio client (Interactions API TTS and music generation)."""

    _speak_endpoint = config.GoogleInteractionsEndpoint.CREATE_INTERACTION
    _generate_endpoint = config.GoogleInteractionsEndpoint.CREATE_INTERACTION

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[AudioContent]]:
        return GOOGLE_PARAMETER_MAPPERS

    def _init_request(self, inputs: AudioInput) -> dict[str, Any]:
        """Initialize request with text input."""
        return {
            "input": inputs.text,
            "response_format": {"type": "audio"},
        }

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> AudioArtifact:
        """Parse the audio artifact from the model_output step."""
        steps = super()._parse_content(response_data)
        for step in steps:
            if step.get("type") != "model_output":
                continue
            for part in step.get("content", []):
                if part.get("type") != "audio" or not part.get("data"):
                    continue
                metadata = {
                    k: part[k] for k in ("sample_rate", "channels") if part.get(k)
                }
                return AudioArtifact(
                    data=part["data"],
                    mime_type=_to_audio_mime(part.get("mime_type")),
                    metadata=metadata,
                )
        msg = "No audio content in response"
        raise ValueError(msg)

    def _stream_class(self) -> type[AudioStream]:
        """Return the Stream class for this provider."""
        return GoogleAudioStream


__all__ = ["GoogleAudioClient", "GoogleAudioStream"]
