"""OpenAI audio client."""

from typing import Any

from celeste.artifacts import AudioArtifact
from celeste.mime_types import AudioMimeType
from celeste.parameters import ParameterMapper
from celeste.providers.openai.audio import config
from celeste.providers.openai.audio.client import OpenAIAudioClient as OpenAIAudioMixin
from celeste.types import AudioContent

from ...client import AudioClient
from ...io import AudioFinishReason, AudioInput
from .parameters import OPENAI_PARAMETER_MAPPERS


class OpenAIAudioClient(OpenAIAudioMixin, AudioClient):
    """OpenAI audio client (TTS and speech-to-text)."""

    _speak_endpoint = config.OpenAIAudioEndpoint.CREATE_SPEECH
    _transcribe_endpoint = config.OpenAIAudioEndpoint.CREATE_TRANSCRIPTION

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[AudioContent]]:
        return OPENAI_PARAMETER_MAPPERS

    def _init_request(self, inputs: AudioInput) -> dict[str, Any]:
        """Initialize TTS text input or transcription file payload."""
        if inputs.audio is not None:
            audio = inputs.audio
            if isinstance(audio, list):
                if len(audio) != 1:
                    msg = "OpenAI transcription accepts exactly one audio file"
                    raise ValueError(msg)
                artifact = audio[0]
            else:
                artifact = audio
            if not isinstance(artifact, AudioArtifact):
                msg = "OpenAI transcription requires an AudioArtifact"
                raise ValueError(msg)
            return {"file": artifact}
        return {"input": inputs.text}

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> AudioArtifact | str:
        """Extract audio bytes for TTS or transcript text for STT."""
        if "audio_bytes" in response_data:
            audio_bytes = response_data.get("audio_bytes")
            if not audio_bytes:
                msg = "No audio data in response"
                raise ValueError(msg)
            content_type = (
                response_data.get("headers", {})
                .get("content-type", "")
                .split(";", 1)[0]
                .strip()
                .lower()
            )
            try:
                mime_type = AudioMimeType(content_type)
            except ValueError:
                response_format = response_data.get("response_format")
                mime_type = (
                    self._map_response_format_to_mime_type(response_format)
                    if response_format
                    else None
                )
            return AudioArtifact(data=audio_bytes, mime_type=mime_type)
        return super()._parse_content(response_data)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> AudioFinishReason:
        """OpenAI Audio API doesn't provide finish reasons."""
        _ = response_data
        return AudioFinishReason(reason=None)


__all__ = ["OpenAIAudioClient"]
