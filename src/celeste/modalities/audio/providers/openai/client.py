"""OpenAI audio client."""

from typing import Any, Unpack

from celeste.artifacts import AudioArtifact
from celeste.parameters import ParameterMapper
from celeste.providers.openai.audio import config
from celeste.providers.openai.audio.client import OpenAIAudioClient as OpenAIAudioMixin

from ...client import AudioClient
from ...io import AudioFinishReason, AudioInput, AudioOutput, AudioUsage
from ...parameters import AudioParameters
from .parameters import OPENAI_PARAMETER_MAPPERS


class OpenAIAudioClient(OpenAIAudioMixin, AudioClient):
    """OpenAI audio client (TTS)."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return OPENAI_PARAMETER_MAPPERS

    async def speak(
        self,
        text: str,
        **parameters: Unpack[AudioParameters],
    ) -> AudioOutput:
        """Convert text to speech audio."""
        inputs = AudioInput(text=text)
        return await self._predict(
            inputs,
            endpoint=config.OpenAIAudioEndpoint.CREATE_SPEECH,
            **parameters,
        )

    def _init_request(self, inputs: AudioInput) -> dict[str, Any]:
        """Initialize request with text input."""
        return {"input": inputs.text}

    def _parse_usage(self, response_data: dict[str, Any]) -> AudioUsage:
        """Parse usage from response."""
        usage = super()._parse_usage(response_data)
        return AudioUsage(**usage)

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[AudioParameters],
    ) -> AudioArtifact:
        """Extract audio bytes from response."""
        audio_bytes = response_data.get("audio_bytes")
        if not audio_bytes:
            msg = "No audio data in response"
            raise ValueError(msg)

        # Use mixin helper to determine MIME type from output_format
        output_format = parameters.get("output_format")
        mime_type = self._map_response_format_to_mime_type(output_format)

        return AudioArtifact(data=audio_bytes, mime_type=mime_type)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> AudioFinishReason:
        """OpenAI TTS doesn't provide finish reasons."""
        return AudioFinishReason(reason=None)


__all__ = ["OpenAIAudioClient"]
