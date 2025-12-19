"""XAI streaming for text generation."""

from collections.abc import Callable
from typing import Any, Unpack

from celeste_xai.responses.streaming import XAIResponsesStream

from celeste.types import StructuredOutput
from celeste_text_generation.io import (
    TextGenerationChunk,
    TextGenerationFinishReason,
    TextGenerationOutput,
    TextGenerationUsage,
)
from celeste_text_generation.parameters import TextGenerationParameters
from celeste_text_generation.streaming import TextGenerationStream


class XAITextGenerationStream(XAIResponsesStream, TextGenerationStream):
    """XAI streaming for text generation."""

    def __init__(
        self,
        sse_iterator: Any,  # noqa: ANN401
        transform_output: Callable[..., StructuredOutput],
        **parameters: Unpack[TextGenerationParameters],
    ) -> None:
        """Initialize stream."""
        super().__init__(sse_iterator, **parameters)
        self._transform_output = transform_output

    def _parse_chunk(self, event: dict[str, Any]) -> TextGenerationChunk | None:
        """Parse SSE event into typed Chunk."""
        raw = super()._parse_chunk(event)
        if not raw:
            return None

        usage = TextGenerationUsage(**raw["usage"]) if raw["usage"] else None
        finish_reason = (
            TextGenerationFinishReason(reason=raw["finish_reason"])
            if raw["finish_reason"]
            else None
        )

        return TextGenerationChunk(
            content=raw["content"],
            finish_reason=finish_reason,
            usage=usage,
            metadata={"raw_event": raw["raw_event"]},
        )

    def _parse_usage(self, chunks: list[TextGenerationChunk]) -> TextGenerationUsage:
        """Extract usage from final chunk."""
        for chunk in reversed(chunks):
            if chunk.usage:
                return chunk.usage
        return TextGenerationUsage()

    def _parse_output(
        self,
        chunks: list[TextGenerationChunk],
        **parameters: Unpack[TextGenerationParameters],
    ) -> TextGenerationOutput:
        """Assemble chunks into final output."""
        content = "".join(chunk.content for chunk in chunks)
        content = self._transform_output(content, **parameters)
        usage = self._parse_usage(chunks)
        finish_reason = chunks[-1].finish_reason if chunks else None

        raw_response = None
        for chunk in reversed(chunks):
            raw_event = chunk.metadata.get("raw_event", {})
            if raw_event.get("type") == "response.completed":
                raw_response = raw_event.get("response")
                break

        return TextGenerationOutput(
            content=content,
            usage=usage,
            finish_reason=finish_reason,
            metadata={"raw_response": raw_response},
        )


__all__ = ["XAITextGenerationStream"]
