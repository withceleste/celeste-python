"""Streaming for text generation."""

from abc import abstractmethod
from typing import Any, Unpack

from celeste.io import Chunk
from celeste.streaming import Stream
from celeste_text_generation.io import (
    TextGenerationChunk,
    TextGenerationOutput,
    TextGenerationUsage,
)
from celeste_text_generation.parameters import TextGenerationParameters


class TextGenerationStream(Stream[TextGenerationOutput, TextGenerationParameters]):
    """Streaming for text generation."""

    @abstractmethod
    def _parse_chunk(self, event: dict[str, Any]) -> Chunk | None:
        """Parse SSE event into Chunk (provider-specific)."""
        ...

    def _parse_output(
        self,
        chunks: list[TextGenerationChunk],
        **parameters: Unpack[TextGenerationParameters],
    ) -> TextGenerationOutput:
        """Assemble chunks into final output."""
        content = "".join(chunk.content for chunk in chunks)
        usage = self._parse_usage(chunks)
        finish_reason = chunks[-1].finish_reason if chunks else None

        return TextGenerationOutput(
            content=content,
            usage=usage,
            metadata={"finish_reason": finish_reason},
        )

    @abstractmethod
    def _parse_usage(self, chunks: list[TextGenerationChunk]) -> TextGenerationUsage:
        """Parse usage from chunks (provider-specific)."""


__all__ = ["TextGenerationStream"]
