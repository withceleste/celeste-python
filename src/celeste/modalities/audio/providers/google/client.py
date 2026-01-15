"""Google audio client."""

import base64
from typing import Any, Unpack

from celeste.artifacts import AudioArtifact
from celeste.mime_types import AudioMimeType
from celeste.parameters import ParameterMapper
from celeste.providers.google.cloud_tts import config
from celeste.providers.google.cloud_tts.client import (
    GoogleCloudTTSClient as GoogleCloudTTSMixin,
)

from ...client import AudioClient
from ...io import (
    AudioFinishReason,
    AudioInput,
    AudioOutput,
    AudioUsage,
)
from ...parameters import AudioParameter, AudioParameters
from .parameters import GOOGLE_PARAMETER_MAPPERS


class GoogleAudioClient(GoogleCloudTTSMixin, AudioClient):
    """Google audio client (Cloud TTS)."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return GOOGLE_PARAMETER_MAPPERS

    async def speak(
        self,
        text: str,
        **parameters: Unpack[AudioParameters],
    ) -> AudioOutput:
        """Convert text to speech audio."""
        inputs = AudioInput(text=text)
        return await self._predict(
            inputs,
            endpoint=config.GoogleCloudTTSEndpoint.CREATE_SPEECH,
            **parameters,
        )

    def _init_request(self, inputs: AudioInput) -> dict[str, Any]:
        """Initialize request with text input."""
        return {
            "input": {"text": inputs.text},
            "voice": {"modelName": self.model.id},
            "audioConfig": {},
        }

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
        audio_b64 = super()._parse_content(response_data)
        audio_bytes = base64.b64decode(audio_b64)

        output_format = parameters.get(AudioParameter.OUTPUT_FORMAT)
        mime_type = AudioMimeType(output_format) if output_format else AudioMimeType.MP3

        return AudioArtifact(data=audio_bytes, mime_type=mime_type)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> AudioFinishReason:
        """Parse finish reason from response."""
        finish_reason = super()._parse_finish_reason(response_data)
        return AudioFinishReason(reason=finish_reason.reason)


__all__ = ["GoogleAudioClient"]
