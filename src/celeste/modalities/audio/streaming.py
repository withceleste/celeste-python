"""Audio streaming primitives."""

from abc import abstractmethod

from celeste.artifacts import AudioArtifact
from celeste.streaming import Stream

from .io import (
    AudioChunk,
    AudioFinishReason,
    AudioOutput,
    AudioUsage,
)
from .parameters import AudioParameters


class AudioStream(Stream[AudioOutput, AudioParameters, AudioChunk]):
    """Streaming for audio modality."""

    _usage_class = AudioUsage
    _finish_reason_class = AudioFinishReason
    _chunk_class = AudioChunk
    _output_class = AudioOutput
    _empty_content = b""

    @abstractmethod
    def _aggregate_content(self, chunks: list[AudioChunk]) -> AudioArtifact:
        """Aggregate content from chunks into AudioArtifact."""
        ...


__all__ = ["AudioStream"]
