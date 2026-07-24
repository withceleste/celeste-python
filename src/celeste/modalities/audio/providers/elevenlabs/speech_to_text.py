"""ElevenLabs speech-to-text audio backend."""

from typing import Any

from celeste.artifacts import AudioArtifact
from celeste.parameters import ParameterMapper
from celeste.providers.elevenlabs.speech_to_text import config
from celeste.providers.elevenlabs.speech_to_text.client import (
    ElevenLabsSpeechToTextClient as ElevenLabsSpeechToTextMixin,
)
from celeste.types import AudioContent

from ...client import AudioClient
from ...io import AudioFinishReason, AudioInput
from .parameters import ELEVENLABS_SPEECH_TO_TEXT_PARAMETER_MAPPERS


class ElevenLabsSpeechToTextAudioClient(ElevenLabsSpeechToTextMixin, AudioClient):
    """ElevenLabs audio client (speech-to-text)."""

    _transcribe_endpoint = config.ElevenLabsSpeechToTextEndpoint.CREATE_TRANSCRIPTION

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[AudioContent]]:
        return ELEVENLABS_SPEECH_TO_TEXT_PARAMETER_MAPPERS

    def _init_request(self, inputs: AudioInput) -> dict[str, Any]:
        """Initialize multipart transcription request with audio file."""
        audio = inputs.audio
        if audio is None:
            msg = "Audio input is required for transcription"
            raise ValueError(msg)
        if isinstance(audio, list):
            if len(audio) != 1:
                msg = "ElevenLabs transcription accepts exactly one audio file"
                raise ValueError(msg)
            artifact = audio[0]
        else:
            artifact = audio
        if not isinstance(artifact, AudioArtifact):
            msg = "ElevenLabs transcription requires an AudioArtifact"
            raise ValueError(msg)
        return {"file": artifact}

    def _parse_content(self, response_data: dict[str, Any]) -> str:
        """Extract transcript text from response."""
        return super()._parse_content(response_data)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> AudioFinishReason:
        """ElevenLabs STT does not provide finish reasons."""
        _ = response_data
        return AudioFinishReason(reason=None)


__all__ = ["ElevenLabsSpeechToTextAudioClient"]
