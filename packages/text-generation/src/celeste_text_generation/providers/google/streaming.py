"""Google streaming for text generation."""

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


class GoogleTextGenerationStream(TextGenerationStream):
    """Google streaming for text generation."""

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
        """Parse SSE event into Chunk.

        Extract text delta from candidates[0].content.parts[0].text.
        Extract finishReason and usageMetadata if present.
        Return None if no text delta (filter lifecycle events).
        """
        # Extract candidates array
        candidates = event.get("candidates", [])
        if not candidates:
            return None

        candidate = candidates[0]
        content = candidate.get("content", {})
        parts = content.get("parts", [])

        # Extract text delta
        text_delta = None
        if parts:
            text_part = parts[0]
            text_delta = text_part.get("text")

        # If no text delta, this is likely a lifecycle event - filter it
        if not text_delta:
            return None

        # Extract finish reason if present
        finish_reason: TextGenerationFinishReason | None = None
        finish_reason_str = candidate.get("finishReason")
        if finish_reason_str:
            finish_reason = TextGenerationFinishReason(reason=finish_reason_str)

        # Extract usage metadata if present (store in chunk metadata for later)
        usage: TextGenerationUsage | None = None
        usage_metadata = event.get("usageMetadata")
        if usage_metadata:
            usage = TextGenerationUsage(
                input_tokens=usage_metadata.get("promptTokenCount"),
                output_tokens=usage_metadata.get("candidatesTokenCount"),
                total_tokens=usage_metadata.get("totalTokenCount"),
                reasoning_tokens=usage_metadata.get("thoughtsTokenCount"),
            )

        return TextGenerationChunk(
            content=text_delta,
            finish_reason=finish_reason,
            usage=usage,
        )

    def _parse_usage(self, chunks: list[TextGenerationChunk]) -> TextGenerationUsage:
        """Parse usage from chunks.

        Google provides usageMetadata in the final chunk(s).
        Accumulate usage from all chunks, prioritizing later chunks for totals.
        """
        if not chunks:
            return TextGenerationUsage()

        # Usage metadata is typically in the final chunk
        final_chunk = chunks[-1]
        if final_chunk.usage:
            # Return final chunk usage directly (contains complete usageMetadata)
            return final_chunk.usage

        # Fallback: check metadata if stored there
        usage_metadata = final_chunk.metadata.get("usageMetadata")
        if usage_metadata:
            return TextGenerationUsage(
                input_tokens=usage_metadata.get("promptTokenCount"),
                output_tokens=usage_metadata.get("candidatesTokenCount"),
                total_tokens=usage_metadata.get("totalTokenCount"),
                reasoning_tokens=usage_metadata.get("thoughtsTokenCount"),
            )

        # Accumulate usage from chunks that have usage metadata
        total_input_tokens = 0
        total_output_tokens = 0
        total_reasoning_tokens = 0
        total_total_tokens = 0

        for chunk in chunks:
            if chunk.usage:
                if chunk.usage.input_tokens is not None:
                    total_input_tokens = chunk.usage.input_tokens  # Use latest value
                if chunk.usage.output_tokens is not None:
                    total_output_tokens = chunk.usage.output_tokens  # Use latest value
                if chunk.usage.reasoning_tokens is not None:
                    total_reasoning_tokens = (
                        chunk.usage.reasoning_tokens
                    )  # Use latest value
                if chunk.usage.total_tokens is not None:
                    total_total_tokens = chunk.usage.total_tokens  # Use latest value

        return TextGenerationUsage(
            input_tokens=total_input_tokens if total_input_tokens > 0 else None,
            output_tokens=total_output_tokens if total_output_tokens > 0 else None,
            total_tokens=total_total_tokens if total_total_tokens > 0 else None,
            reasoning_tokens=total_reasoning_tokens
            if total_reasoning_tokens > 0
            else None,
        )

    def _parse_output(
        self,
        chunks: list[TextGenerationChunk],
        **parameters: Unpack[TextGenerationParameters],
    ) -> TextGenerationOutput:
        """Assemble chunks into final output with structured output support.

        Concatenates text chunks, then applies parameter transformations
        (e.g., JSON → BaseModel if output_schema provided).
        """
        # Concatenate text chunks
        content = "".join(chunk.content for chunk in chunks)

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


__all__ = ["GoogleTextGenerationStream"]
