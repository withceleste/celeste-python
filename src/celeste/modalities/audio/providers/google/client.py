"""Google audio client."""

from typing import Any

from celeste.artifacts import AudioArtifact
from celeste.parameters import ParameterMapper
from celeste.providers.google.cloud_tts import config
from celeste.providers.google.cloud_tts.client import (
    GoogleCloudTTSClient as GoogleCloudTTSMixin,
)
from celeste.types import AudioContent

from ...client import AudioClient
from ...io import (
    AudioInput,
)
from .parameters import GOOGLE_PARAMETER_MAPPERS


class GoogleAudioClient(GoogleCloudTTSMixin, AudioClient):
    """Google audio client (Cloud TTS)."""

    _speak_endpoint = config.GoogleCloudTTSEndpoint.CREATE_SPEECH

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[AudioContent]]:
        return GOOGLE_PARAMETER_MAPPERS

    def _init_request(self, inputs: AudioInput) -> dict[str, Any]:
        """Initialize request with text input."""
        return {
            "input": {"text": inputs.text},
            "voice": {"modelName": self.model.id},
            "audioConfig": {},
        }

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> AudioArtifact:
        """Extract audio bytes from response."""
        audio_b64 = super()._parse_content(response_data)
        return AudioArtifact(data=audio_b64)


__all__ = ["GoogleAudioClient"]
