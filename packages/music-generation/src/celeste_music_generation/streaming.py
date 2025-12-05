"""Streaming support for music generation."""

from typing import Unpack

from celeste.streaming import Stream
from celeste_music_generation.io import (
    MusicGenerationChunk,
    MusicGenerationOutput,
    MusicGenerationUsage,
)
from celeste_music_generation.parameters import MusicGenerationParameters


class MusicGenerationStream(
    Stream[MusicGenerationOutput, MusicGenerationParameters, MusicGenerationChunk]
):
    """Async stream for music generation.

    For task-based providers (like Mureka), this stream handles:
    - Polling for task status updates
    - Progressive streaming when available (stream_url)
    - Final result delivery

    Yields MusicGenerationChunk objects with task status and content updates.
    """

    def _parse_output(  # type: ignore[override]
        self,
        chunks: list[MusicGenerationChunk],
        **parameters: Unpack[MusicGenerationParameters],
    ) -> MusicGenerationOutput:
        """Assemble chunks into final output.

        For music generation, the final chunk contains the complete audio.
        Progressive chunks may contain partial audio or status updates.
        """
        if not chunks:
            msg = "No chunks received from stream"
            raise ValueError(msg)

        # Final chunk contains complete audio
        content = chunks[-1].content
        usage = self._parse_usage(chunks)
        finish_reason = chunks[-1].finish_reason if chunks else None

        return MusicGenerationOutput(
            content=content,
            usage=usage,
            finish_reason=finish_reason,
            metadata={},
        )

    def _parse_usage(self, chunks: list[MusicGenerationChunk]) -> MusicGenerationUsage:
        """Parse usage from chunks.

        For task-based providers, usage info is typically in the final chunk.
        """
        for chunk in reversed(chunks):
            if chunk.usage:
                return chunk.usage

        return MusicGenerationUsage()


__all__ = ["MusicGenerationStream"]
