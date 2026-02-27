"""Google audio client."""

from typing import Any, Unpack

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
    AudioOutput,
)
from ...parameters import AudioParameters
from .parameters import GOOGLE_PARAMETER_MAPPERS


class GoogleAudioClient(GoogleCloudTTSMixin, AudioClient):
    """Google audio client (Cloud TTS)."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[AudioContent]]:
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

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> AudioArtifact:
        """Extract audio bytes from response."""
        audio_b64 = super()._parse_content(response_data)
        return AudioArtifact(data=audio_b64)


__all__ = ["GoogleAudioClient"]
