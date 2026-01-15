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
    AudioFinishReason,
    AudioInput,
    AudioOutput,
    AudioUsage,
)
from ...parameters import AudioParameters
from ...streaming import AudioStream
from .parameters import ELEVENLABS_PARAMETER_MAPPERS


class ElevenLabsAudioStream(_ElevenLabsTextToSpeechStream, AudioStream):
    """ElevenLabs streaming for audio modality."""

    def _parse_chunk_usage(self, event_data: dict[str, Any]) -> AudioUsage | None:
        """Parse and wrap usage from event."""
        usage = super()._parse_chunk_usage(event_data)
        if usage:
            return AudioUsage(**usage)
        return None

    def _parse_chunk_finish_reason(
        self, event_data: dict[str, Any]
    ) -> AudioFinishReason | None:
        """Parse and wrap finish reason from event."""
        finish_reason = super()._parse_chunk_finish_reason(event_data)
        if finish_reason:
            return AudioFinishReason(reason=finish_reason.reason)
        return None

    def _parse_chunk(self, event_data: dict[str, Any]) -> AudioChunk | None:
        """Parse binary audio chunk from stream event."""
        chunk_data = self._parse_chunk_content(event_data)
        if not chunk_data:
            usage = self._parse_chunk_usage(event_data)
            finish_reason = self._parse_chunk_finish_reason(event_data)
            if usage is None and finish_reason is None:
                return None
            # Chunk with usage/finish_reason only (no audio)
            return AudioChunk(
                content=b"",
                finish_reason=finish_reason,
                usage=usage,
                metadata={"event_data": event_data},
            )

        return AudioChunk(
            content=chunk_data,
            finish_reason=self._parse_chunk_finish_reason(event_data),
            usage=self._parse_chunk_usage(event_data),
            metadata={"event_data": event_data},
        )

    def _aggregate_content(self, chunks: list[AudioChunk]) -> AudioArtifact:
        """Aggregate audio content from chunks into AudioArtifact."""
        audio_bytes = b"".join(chunk.content for chunk in chunks if chunk.content)
        # Get mime_type from output_format parameter via client
        output_format = self._parameters.get("output_format")
        client: ElevenLabsAudioClient = self._client
        mime_type = client._map_output_format_to_mime_type(output_format)
        return AudioArtifact(data=audio_bytes, mime_type=mime_type)

    def _aggregate_event_data(self, chunks: list[AudioChunk]) -> list[dict[str, Any]]:
        """Collect raw events (filtering happens in _build_stream_metadata)."""
        events: list[dict[str, Any]] = []
        for chunk in chunks:
            event_data = chunk.metadata.get("event_data")
            if isinstance(event_data, dict):
                events.append(event_data)
        return events


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

        output_format = parameters.get("output_format")
        mime_type = self._map_output_format_to_mime_type(output_format)

        return AudioArtifact(data=audio_bytes, mime_type=mime_type)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> AudioFinishReason:
        """Parse finish reason from response."""
        finish_reason = super()._parse_finish_reason(response_data)
        return AudioFinishReason(reason=finish_reason.reason)

    def _stream_class(self) -> type[AudioStream]:
        """Return the Stream class for this provider."""
        return ElevenLabsAudioStream


__all__ = ["ElevenLabsAudioClient", "ElevenLabsAudioStream"]
