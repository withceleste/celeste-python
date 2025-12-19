"""Google client implementation for speech generation."""

import base64
from typing import Any, Unpack

from celeste_google.cloud_tts.client import GoogleCloudTTSClient

from celeste.artifacts import AudioArtifact
from celeste.mime_types import AudioMimeType
from celeste.parameters import ParameterMapper
from celeste_speech_generation.client import SpeechGenerationClient
from celeste_speech_generation.io import (
    SpeechGenerationInput,
    SpeechGenerationUsage,
)
from celeste_speech_generation.parameters import (
    SpeechGenerationParameter,
    SpeechGenerationParameters,
)

from .parameters import GOOGLE_PARAMETER_MAPPERS


class GoogleSpeechGenerationClient(GoogleCloudTTSClient, SpeechGenerationClient):
    """Google client for speech generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return GOOGLE_PARAMETER_MAPPERS

    def _init_request(self, inputs: SpeechGenerationInput) -> dict[str, Any]:
        """Initialize request from Cloud TTS API format."""
        return {
            "input": {"text": inputs.text},
            "voice": {"modelName": self.model.id},
            "audioConfig": {},
        }

    def _parse_usage(self, response_data: dict[str, Any]) -> SpeechGenerationUsage:
        """Parse usage from response."""
        usage = super()._parse_usage(response_data)
        return SpeechGenerationUsage(**usage)

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[SpeechGenerationParameters],
    ) -> AudioArtifact:
        """Parse content from response."""
        audio_b64 = super()._parse_content(response_data)
        audio_bytes = base64.b64decode(audio_b64)

        # Get output_format from parameters, default to MP3
        output_format = parameters.get(SpeechGenerationParameter.OUTPUT_FORMAT)
        mime_type = self._get_mime_type(output_format)

        return AudioArtifact(
            data=audio_bytes,
            mime_type=mime_type,
            metadata={"format": str(mime_type)},
        )

    def _get_mime_type(self, output_format: str | None) -> AudioMimeType:
        """Get AudioMimeType from output_format parameter."""
        if output_format is None:
            return AudioMimeType.MP3

        return AudioMimeType(output_format)


__all__ = ["GoogleSpeechGenerationClient"]
