"""OpenAI audio client."""

from typing import Any

from celeste.artifacts import AudioArtifact
from celeste.parameters import ParameterMapper
from celeste.providers.openai.audio import config
from celeste.providers.openai.audio.client import OpenAIAudioClient as OpenAIAudioMixin
from celeste.types import AudioContent

from ...client import AudioClient
from ...io import AudioFinishReason, AudioInput
from .parameters import OPENAI_PARAMETER_MAPPERS


class OpenAIAudioClient(OpenAIAudioMixin, AudioClient):
    """OpenAI audio client (TTS)."""

    _speak_endpoint = config.OpenAIAudioEndpoint.CREATE_SPEECH

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[AudioContent]]:
        return OPENAI_PARAMETER_MAPPERS

    def _init_request(self, inputs: AudioInput) -> dict[str, Any]:
        """Initialize request with text input."""
        return {"input": inputs.text}

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> AudioArtifact:
        """Extract audio bytes from response."""
        audio_bytes = response_data.get("audio_bytes")
        if not audio_bytes:
            msg = "No audio data in response"
            raise ValueError(msg)

        return AudioArtifact(data=audio_bytes)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> AudioFinishReason:
        """OpenAI TTS doesn't provide finish reasons."""
        return AudioFinishReason(reason=None)


__all__ = ["OpenAIAudioClient"]
