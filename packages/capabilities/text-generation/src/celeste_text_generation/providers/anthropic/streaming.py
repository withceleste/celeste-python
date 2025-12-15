"""Anthropic streaming for text generation."""

from collections.abc import Callable
from typing import Any, Unpack

from celeste_anthropic.messages.streaming import AnthropicMessagesStream

from celeste.types import StructuredOutput
from celeste_text_generation.io import (
    TextGenerationChunk,
    TextGenerationFinishReason,
    TextGenerationOutput,
    TextGenerationUsage,
)
from celeste_text_generation.parameters import TextGenerationParameters
from celeste_text_generation.streaming import TextGenerationStream


class AnthropicTextGenerationStream(AnthropicMessagesStream, TextGenerationStream):
    """Anthropic streaming for text generation."""

    def __init__(
        self,
        sse_iterator: Any,  # noqa: ANN401
        transform_output: Callable[..., StructuredOutput],
        **parameters: Unpack[TextGenerationParameters],
    ) -> None:
        """Initialize stream with output transformation support."""
        super().__init__(sse_iterator, **parameters)
        self._transform_output = transform_output
        self._last_finish_reason: TextGenerationFinishReason | None = None

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

        if finish_reason:
            self._last_finish_reason = finish_reason

        # For message_stop events, use stored finish_reason
        event_type = raw["raw_event"].get("type")
        if event_type == "message_stop" and self._last_finish_reason:
            finish_reason = self._last_finish_reason

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

        raw_events = [
            c.metadata["raw_event"]
            for c in chunks
            if c.metadata.get("raw_event", {}).get("type")
            in ("message_delta", "message_stop")
        ]

        return TextGenerationOutput(
            content=content,
            usage=usage,
            finish_reason=finish_reason,
            metadata={"raw_response": raw_events},
        )


__all__ = ["AnthropicTextGenerationStream"]
