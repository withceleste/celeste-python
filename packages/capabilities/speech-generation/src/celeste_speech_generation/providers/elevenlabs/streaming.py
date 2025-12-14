"""ElevenLabs streaming for speech generation."""

from typing import Any

from celeste_speech_generation.io import (
    SpeechGenerationChunk,
    SpeechGenerationUsage,
)
from celeste_speech_generation.streaming import SpeechGenerationStream


class ElevenLabsSpeechGenerationStream(SpeechGenerationStream):
    """ElevenLabs streaming for speech generation."""

    def _parse_chunk(self, event: dict[str, Any]) -> SpeechGenerationChunk | None:
        """Parse binary audio chunk from event dict.

        Event dict contains {"data": bytes} for binary audio chunks.
        """
        audio_bytes = event.get("data")
        if audio_bytes is None:
            return None

        if not isinstance(audio_bytes, bytes):
            return None

        # Return chunk with binary audio data
        return SpeechGenerationChunk(
            content=audio_bytes,
            usage=None,  # Usage calculated in _parse_usage()
            metadata={"content_length": len(audio_bytes)},
        )

    def _parse_usage(
        self, chunks: list[SpeechGenerationChunk]
    ) -> SpeechGenerationUsage:
        """Parse usage from chunks.

        ElevenLabs doesn't return usage in streaming response.
        """
        return SpeechGenerationUsage()


__all__ = ["ElevenLabsSpeechGenerationStream"]
