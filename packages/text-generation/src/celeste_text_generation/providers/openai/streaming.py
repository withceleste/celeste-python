"""OpenAI streaming for text generation."""

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


class OpenAITextGenerationStream(TextGenerationStream):
    """OpenAI streaming for text generation."""

    def __init__(
        self,
        sse_iterator: Any,  # noqa: ANN401
        transform_output: Callable[..., object],
        **parameters: Unpack[TextGenerationParameters],
    ) -> None:
        """Initialize stream."""
        super().__init__(sse_iterator, **parameters)
        self._transform_output = transform_output

    def _parse_chunk(self, event: dict[str, Any]) -> TextGenerationChunk | None:
        """Parse SSE event into Chunk."""
        event_type = event.get("type")
        if not event_type:
            return None

        if event_type == "response.output_text.delta":
            delta = event.get("delta")
            if delta is None:
                return None
            return TextGenerationChunk(
                content=delta,
                finish_reason=None,
                usage=None,
            )

        if event_type == "response.output_text.done":
            return None

        if event_type == "response.completed":
            response_data = event.get("response", {})
            usage_data = response_data.get("usage")

            usage: TextGenerationUsage | None = None
            if usage_data:
                input_tokens_details = usage_data.get("input_tokens_details", {})
                output_tokens_details = usage_data.get("output_tokens_details", {})
                usage = TextGenerationUsage(
                    input_tokens=usage_data.get("input_tokens"),
                    output_tokens=usage_data.get("output_tokens"),
                    total_tokens=usage_data.get("total_tokens"),
                    cached_tokens=input_tokens_details.get("cached_tokens"),
                    reasoning_tokens=output_tokens_details.get("reasoning_tokens"),
                    billed_tokens=None,
                )

            finish_reason: TextGenerationFinishReason | None = None
            status = response_data.get("status")
            if status == "completed":
                finish_reason = TextGenerationFinishReason(reason="completed")

            return TextGenerationChunk(
                content="",
                finish_reason=finish_reason,
                usage=usage,
            )

        return None

    def _parse_usage(self, chunks: list[TextGenerationChunk]) -> TextGenerationUsage:
        """Parse usage from chunks."""
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
        """Assemble chunks into final output."""
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


__all__ = ["OpenAITextGenerationStream"]
