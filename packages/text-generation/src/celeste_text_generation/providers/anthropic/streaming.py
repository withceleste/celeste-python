"""Anthropic streaming for text generation."""

from collections.abc import Callable
from typing import Any, Unpack

from celeste_text_generation.io import (
    TextGenerationChunk,
    TextGenerationFinishReason,
    TextGenerationOutput,
    TextGenerationUsage,
)
from celeste_text_generation.parameters import TextGenerationParameters
from celeste_text_generation.streaming import TextGenerationStream


class AnthropicTextGenerationStream(TextGenerationStream):
    """Anthropic streaming for text generation."""

    def __init__(
        self,
        sse_iterator: Any,  # noqa: ANN401
        transform_output: Callable[..., object],
        **parameters: Unpack[TextGenerationParameters],
    ) -> None:
        """Initialize stream with output transformation support.

        Args:
            sse_iterator: Server-Sent Events iterator.
            transform_output: Function to transform accumulated content (e.g., JSON → BaseModel).
            **parameters: Parameters passed to stream() for output transformation.
        """
        super().__init__(sse_iterator, **parameters)
        self._transform_output = transform_output
        self._last_finish_reason: TextGenerationFinishReason | None = None

    def _parse_chunk(self, event: dict[str, Any]) -> TextGenerationChunk | None:
        """Parse SSE event into Chunk."""
        event_type = event.get("type")
        if not event_type:
            return None

        if event_type == "content_block_delta":
            delta = event.get("delta", {})
            if delta.get("type") == "text_delta":
                text_delta = delta.get("text")
                if text_delta is not None:
                    return TextGenerationChunk(
                        content=text_delta,
                        finish_reason=None,
                        usage=None,
                    )

        if event_type == "message_delta":
            delta = event.get("delta", {})
            stop_reason = delta.get("stop_reason")

            finish_reason: TextGenerationFinishReason | None = None
            if stop_reason is not None:
                finish_reason = TextGenerationFinishReason(reason=stop_reason)
                self._last_finish_reason = finish_reason

            usage = self._parse_usage_from_event(event)

            return TextGenerationChunk(
                content="",
                finish_reason=finish_reason,
                usage=usage,
            )

        # Parse message stop event (final event)
        if event_type == "message_stop":
            usage = self._parse_usage_from_event(event)

            return TextGenerationChunk(
                content="",
                finish_reason=self._last_finish_reason,
                usage=usage,
            )

        # Ignore other event types
        return None

    def _parse_usage_from_event(
        self, event: dict[str, Any]
    ) -> TextGenerationUsage | None:
        """Parse usage from SSE event data.

        Args:
            event: SSE event dictionary containing usage data.

        Returns:
            TextGenerationUsage object if usage data present, None otherwise.
        """
        usage_data = event.get("usage")
        if not usage_data:
            return None

        input_tokens = usage_data.get("input_tokens")
        output_tokens = usage_data.get("output_tokens")
        total_tokens = None
        if input_tokens is not None and output_tokens is not None:
            total_tokens = input_tokens + output_tokens

        return TextGenerationUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            billed_tokens=None,
            cached_tokens=None,
            reasoning_tokens=None,
        )

    def _parse_usage(self, chunks: list[TextGenerationChunk]) -> TextGenerationUsage:
        """Parse usage from chunks."""
        if not chunks:
            return TextGenerationUsage()

        # Usage typically appears in message_delta or message_stop events
        # Search backwards for the most recent usage
        for chunk in reversed(chunks):
            if chunk.usage:
                return chunk.usage

        return TextGenerationUsage()

    def _parse_output(
        self,
        chunks: list[TextGenerationChunk],
        **parameters: Unpack[TextGenerationParameters],
    ) -> TextGenerationOutput:
        """Assemble chunks into final output with structured output support."""
        content = "".join(chunk.content for chunk in chunks)
        content = self._transform_output(content, **parameters)

        usage = self._parse_usage(chunks)
        finish_reason = chunks[-1].finish_reason if chunks else None

        return TextGenerationOutput(
            content=content,
            usage=usage,
            finish_reason=finish_reason,
            metadata={},
        )


__all__ = ["AnthropicTextGenerationStream"]
