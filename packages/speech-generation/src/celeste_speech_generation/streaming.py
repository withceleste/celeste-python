"""Streaming for speech generation."""

from abc import abstractmethod
from typing import Unpack

from celeste.artifacts import AudioArtifact
from celeste.streaming import Stream
from celeste_speech_generation.io import (
    SpeechGenerationChunk,
    SpeechGenerationOutput,
    SpeechGenerationUsage,
)
from celeste_speech_generation.parameters import SpeechGenerationParameters


class SpeechGenerationStream(
    Stream[SpeechGenerationOutput, SpeechGenerationParameters, SpeechGenerationChunk]
):
    """Streaming for speech generation."""

    def _parse_output(  # type: ignore[override]
        self,
        chunks: list[SpeechGenerationChunk],
        **parameters: Unpack[SpeechGenerationParameters],
    ) -> SpeechGenerationOutput:
        """Assemble chunks into final output."""
        # Speech streaming: concatenate raw bytes
        audio_bytes = b"".join(chunk.content for chunk in chunks)
        usage = self._parse_usage(chunks)

        return SpeechGenerationOutput(
            content=AudioArtifact(data=audio_bytes),
            usage=usage,
            metadata={},
        )

    @abstractmethod
    def _parse_usage(
        self, chunks: list[SpeechGenerationChunk]
    ) -> SpeechGenerationUsage:
        """Parse usage from chunks (provider-specific)."""


__all__ = ["SpeechGenerationStream"]
