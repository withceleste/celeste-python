"""Groq audio client."""

from typing import Any

from celeste.artifacts import AudioArtifact
from celeste.parameters import ParameterMapper
from celeste.providers.groq.audio import config
from celeste.providers.groq.audio.client import GroqAudioClient as GroqAudioMixin
from celeste.types import AudioContent

from ...client import AudioClient
from ...io import AudioFinishReason, AudioInput
from .parameters import GROQ_PARAMETER_MAPPERS


class GroqAudioClient(GroqAudioMixin, AudioClient):
    """Groq audio client (speech-to-text)."""

    _transcribe_endpoint = config.GroqAudioEndpoint.CREATE_TRANSCRIPTION

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[AudioContent]]:
        return GROQ_PARAMETER_MAPPERS

    def _init_request(self, inputs: AudioInput) -> dict[str, Any]:
        """Initialize multipart transcription request with audio file."""
        audio = inputs.audio
        if audio is None:
            msg = "Audio input is required for transcription"
            raise ValueError(msg)
        if isinstance(audio, list):
            if len(audio) != 1:
                msg = "Groq transcription accepts exactly one audio file"
                raise ValueError(msg)
            artifact = audio[0]
        else:
            artifact = audio
        if not isinstance(artifact, AudioArtifact):
            msg = "Groq transcription requires an AudioArtifact"
            raise ValueError(msg)
        return {"file": artifact}

    def _parse_content(self, response_data: dict[str, Any]) -> str:
        """Extract transcript text from response."""
        return super()._parse_content(response_data)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> AudioFinishReason:
        """Groq transcription does not provide finish reasons."""
        _ = response_data
        return AudioFinishReason(reason=None)


__all__ = ["GroqAudioClient"]
