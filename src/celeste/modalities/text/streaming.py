"""Text streaming primitives."""

from celeste.streaming import Stream

from .io import TextChunk, TextFinishReason, TextOutput, TextUsage
from .parameters import TextParameters


class TextStream(Stream[TextOutput, TextParameters, TextChunk]):
    """Streaming for text modality."""

    _usage_class = TextUsage
    _finish_reason_class = TextFinishReason
    _chunk_class = TextChunk
    _output_class = TextOutput
    _empty_content = ""

    def _aggregate_content(self, chunks: list[TextChunk]) -> str:
        """Aggregate content from chunks into raw text."""
        return "".join(chunk.content for chunk in chunks)

    def _aggregate_reasoning(self, chunks: list[TextChunk]) -> str | None:
        """Aggregate reasoning from chunks into text."""
        parts = [c.reasoning for c in chunks if c.reasoning]
        return "".join(parts) if parts else None


__all__ = ["TextStream"]
