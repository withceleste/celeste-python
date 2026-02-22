"""ElevenLabs audio client."""

from typing import Any, Unpack

from celeste.artifacts import AudioArtifact
from celeste.parameters import ParameterMapper
from celeste.providers.elevenlabs.text_to_speech import config
from celeste.providers.elevenlabs.text_to_speech.client import (
    ElevenLabsTextToSpeechClient as ElevenLabsTextToSpeechMixin,
)
from celeste.providers.elevenlabs.text_to_speech.streaming import (
    ElevenLabsTextToSpeechStream as _ElevenLabsTextToSpeechStream,
)

from ...client import AudioClient
from ...io import (
    AudioChunk,
    AudioInput,
    AudioOutput,
)
from ...parameters import AudioParameters
from ...streaming import AudioStream
from .parameters import ELEVENLABS_PARAMETER_MAPPERS


class ElevenLabsAudioStream(_ElevenLabsTextToSpeechStream, AudioStream):
    """ElevenLabs streaming for audio modality."""

    def _aggregate_content(self, chunks: list[AudioChunk]) -> AudioArtifact:
        """Aggregate audio content from chunks into AudioArtifact."""
        audio_bytes = b"".join(chunk.content for chunk in chunks if chunk.content)
        output_format = self._parameters.get("output_format")
        client: ElevenLabsAudioClient = self._client
        mime_type = client._map_output_format_to_mime_type(output_format)
        return AudioArtifact(data=audio_bytes, mime_type=mime_type)


class ElevenLabsAudioClient(ElevenLabsTextToSpeechMixin, AudioClient):
    """ElevenLabs audio client (TTS)."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return ELEVENLABS_PARAMETER_MAPPERS

    async def speak(
        self,
        text: str,
        **parameters: Unpack[AudioParameters],
    ) -> AudioOutput:
        """Convert text to speech audio."""
        inputs = AudioInput(text=text)
        return await self._predict(
            inputs,
            endpoint=config.ElevenLabsTextToSpeechEndpoint.CREATE_SPEECH,
            **parameters,
        )

    def _init_request(self, inputs: AudioInput) -> dict[str, Any]:
        """Initialize request with text input."""
        return {"text": inputs.text}

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

        output_format = parameters.get("output_format")
        mime_type = self._map_output_format_to_mime_type(output_format)

        return AudioArtifact(data=audio_bytes, mime_type=mime_type)

    def _stream_class(self) -> type[AudioStream]:
        """Return the Stream class for this provider."""
        return ElevenLabsAudioStream


__all__ = ["ElevenLabsAudioClient", "ElevenLabsAudioStream"]
