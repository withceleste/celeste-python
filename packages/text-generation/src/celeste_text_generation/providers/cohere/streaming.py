"""Cohere streaming for text generation."""

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


class CohereTextGenerationStream(TextGenerationStream):
    """Cohere streaming for text generation."""

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
        """Parse SSE event into Chunk, extracting text deltas and metadata."""
        event_type = event.get("type")

        if event_type == "content-delta":
            delta = event.get("delta", {})
            message = delta.get("message", {})
            content = message.get("content", {})
            text_delta = content.get("text")

            if not text_delta:
                return None

            return TextGenerationChunk(
                content=text_delta,
                finish_reason=None,
                usage=None,
            )

        if event_type == "message-end":
            delta = event.get("delta", {})
            finish_reason_str = delta.get("finish_reason")
            finish_reason = (
                TextGenerationFinishReason(reason=finish_reason_str)
                if finish_reason_str
                else None
            )

            usage_dict = delta.get("usage", {})
            usage = None
            if isinstance(usage_dict, dict):
                billed_units = usage_dict.get("billed_units", {})
                tokens = usage_dict.get("tokens", {})

                input_tokens = billed_units.get("input_tokens")
                output_tokens = billed_units.get("output_tokens")

                if input_tokens is not None or output_tokens is not None:
                    usage = TextGenerationUsage(
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        total_tokens=tokens.get("total_tokens") if tokens else None,
                        cached_tokens=usage_dict.get("cached_tokens"),
                    )

            return TextGenerationChunk(
                content="",
                finish_reason=finish_reason,
                usage=usage,
            )

        if event_type == "stream-end":
            finish_reason_str = event.get("finish_reason")
            finish_reason = (
                TextGenerationFinishReason(reason=finish_reason_str)
                if finish_reason_str
                else None
            )

            meta = event.get("meta", {})
            usage = None
            if isinstance(meta, dict):
                billed_units = meta.get("billed_units", {})
                tokens = meta.get("tokens", {})

                input_tokens = billed_units.get("input_tokens")
                output_tokens = billed_units.get("output_tokens")

                if input_tokens is not None or output_tokens is not None:
                    usage = TextGenerationUsage(
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        total_tokens=tokens.get("total_tokens") if tokens else None,
                        cached_tokens=meta.get("cached_tokens"),
                    )

            return TextGenerationChunk(
                content="",
                finish_reason=finish_reason,
                usage=usage,
            )

        return None

    def _parse_usage(self, chunks: list[TextGenerationChunk]) -> TextGenerationUsage:
        """Parse usage from chunks, using the last chunk with usage metadata."""
        if not chunks:
            return TextGenerationUsage()

        for chunk in reversed(chunks):
            if chunk.usage:
                return chunk.usage

        return TextGenerationUsage()

    def _parse_output(
        self,
        chunks: list[TextGenerationChunk],
        **parameters: Unpack[TextGenerationParameters],
    ) -> TextGenerationOutput:
        """Assemble chunks into final output, applying parameter transformations."""
        content_chunks = [chunk for chunk in chunks if chunk.content]
        content = "".join(chunk.content for chunk in content_chunks)
        content = self._transform_output(content, **parameters)

        usage = self._parse_usage(chunks)
        finish_reason = chunks[-1].finish_reason if chunks else None

        return TextGenerationOutput(
            content=content,
            usage=usage,
            finish_reason=finish_reason,
            metadata={},
        )


__all__ = ["CohereTextGenerationStream"]
