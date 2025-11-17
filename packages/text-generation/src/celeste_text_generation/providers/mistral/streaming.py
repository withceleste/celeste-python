"""Mistral streaming for text generation."""

import logging
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

logger = logging.getLogger(__name__)


class MistralTextGenerationStream(TextGenerationStream):
    """Mistral streaming for text generation."""

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

    def _parse_chunk(self, event: dict[str, Any]) -> TextGenerationChunk | None:
        """Parse chunk from SSE event.

        Extract from choices[0].delta.content (content delta events).
        Extract finish_reason and usage from final event when finish_reason is not null.
        Return None if no text delta (filter lifecycle events).
        """
        choices = event.get("choices", [])
        if not choices:
            return None

        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            return None

        delta = first_choice.get("delta", {})
        if not isinstance(delta, dict):
            return None

        # Extract content delta
        content_delta = delta.get("content")
        finish_reason_str = first_choice.get("finish_reason")

        # Extract usage from event if present (in final event)
        usage = None
        usage_dict = event.get("usage")
        if isinstance(usage_dict, dict):
            usage = TextGenerationUsage(
                input_tokens=usage_dict.get("prompt_tokens"),
                output_tokens=usage_dict.get("completion_tokens"),
                total_tokens=usage_dict.get("total_tokens"),
            )

        # Create finish reason if present
        finish_reason = (
            TextGenerationFinishReason(reason=finish_reason_str)
            if finish_reason_str
            else None
        )

        # If no content delta and no finish reason, filter this event
        if not content_delta and not finish_reason:
            return None

        return TextGenerationChunk(
            content=content_delta or "",  # Empty string if no content (final event)
            finish_reason=finish_reason,
            usage=usage,
        )

    def _parse_usage(self, chunks: list[TextGenerationChunk]) -> TextGenerationUsage:
        """Parse usage from chunks.

        Mistral provides usage metadata in the final event (when finish_reason is not null).
        Use the last chunk that has usage metadata.
        """
        if not chunks:
            return TextGenerationUsage()

        # Usage metadata is typically in the final chunk (when finish_reason is set)
        for chunk in reversed(chunks):
            if chunk.usage:
                return chunk.usage

        return TextGenerationUsage()

    def _parse_output(
        self,
        chunks: list[TextGenerationChunk],
        **parameters: Unpack[TextGenerationParameters],
    ) -> TextGenerationOutput:
        """Assemble chunks into final output with structured output support.

        Concatenates text chunks, then applies parameter transformations
        (e.g., JSON → BaseModel if output_schema provided).
        """
        # Filter out empty chunks (from final events)
        content_chunks = [chunk for chunk in chunks if chunk.content]

        # Concatenate text chunks
        content = "".join(chunk.content for chunk in content_chunks)

        # Apply parameter transformations (e.g., JSON → BaseModel if output_schema provided)
        content = self._transform_output(content, **parameters)

        usage = self._parse_usage(chunks)
        finish_reason = chunks[-1].finish_reason if chunks else None

        return TextGenerationOutput(
            content=content,
            usage=usage,
            finish_reason=finish_reason,
            metadata={},
        )


__all__ = ["MistralTextGenerationStream"]
