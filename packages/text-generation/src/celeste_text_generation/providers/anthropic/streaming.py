"""Anthropic streaming for text generation."""

import json
from collections.abc import Callable
from typing import Any, Unpack

from celeste.exceptions import ValidationError
from celeste.io import Chunk
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
        transform_output: Callable[[object, Any], object],
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
        # Track tool_use blocks for structured output
        self._tool_use_blocks: list[dict[str, Any]] = []
        self._current_tool_use: dict[str, Any] | None = None
        self._current_tool_use_partial_json: str = ""
        self._last_finish_reason: TextGenerationFinishReason | None = None

    def _parse_chunk(self, event: dict[str, Any]) -> Chunk | None:
        """Parse SSE event into Chunk."""
        event_type = event.get("type")
        if not event_type:
            return None

        # Parse content_block_start for tool_use blocks
        if event_type == "content_block_start":
            content_block = event.get("content_block", {})
            if content_block.get("type") == "tool_use":
                # Initialize new tool_use block
                self._current_tool_use = {
                    "type": "tool_use",
                    "id": content_block.get("id"),
                    "name": content_block.get("name"),
                    "input": {},
                }
                return None  # No chunk yet, waiting for deltas

        # Parse content_block_delta for tool_use and text
        if event_type == "content_block_delta":
            delta = event.get("delta", {})

            # Handle input_json_delta for structured output (Anthropic sends input_json_delta, not tool_use_delta)
            if (
                delta.get("type") == "input_json_delta"
                and self._current_tool_use is not None
            ):
                partial_json = delta.get("partial_json")
                if partial_json is not None:
                    # Accumulate partial JSON string fragments
                    self._current_tool_use_partial_json += partial_json
                    # Emit chunk with accumulated JSON for UI live rendering (only when output_schema is provided)
                    output_schema = self._parameters.get("output_schema")
                    if (
                        output_schema is not None
                        and self._current_tool_use_partial_json
                    ):
                        return TextGenerationChunk(
                            content=self._current_tool_use_partial_json,
                            finish_reason=None,
                            usage=None,
                        )
                    return None

            # Handle tool_use_delta for backward compatibility (older API versions)
            if (
                delta.get("type") == "tool_use_delta"
                and self._current_tool_use is not None
            ):
                partial_json = delta.get("partial_json")
                if partial_json is not None:
                    # Accumulate partial JSON string fragments
                    self._current_tool_use_partial_json += partial_json
                    # Emit chunk with accumulated JSON for UI live rendering (only when output_schema is provided)
                    output_schema = self._parameters.get("output_schema")
                    if (
                        output_schema is not None
                        and self._current_tool_use_partial_json
                    ):
                        return TextGenerationChunk(
                            content=self._current_tool_use_partial_json,
                            finish_reason=None,
                            usage=None,
                        )
                    return None

            # Handle text_delta for regular text content
            if delta.get("type") == "text_delta":
                text_delta = delta.get("text")
                if text_delta is not None:
                    return TextGenerationChunk(
                        content=text_delta,
                        finish_reason=None,
                        usage=None,
                    )

        # Parse content_block_stop to finalize tool_use blocks
        if event_type == "content_block_stop":
            if self._current_tool_use is not None:
                # Tool use block completed - parse accumulated JSON
                tool_id = self._current_tool_use.get("id")
                # Check if we already have this tool_use block from message_start
                existing_block = None
                for block in self._tool_use_blocks:
                    if block.get("id") == tool_id:
                        existing_block = block
                        break

                # Emit final chunk with complete JSON for UI (only when output_schema is provided)
                output_schema = self._parameters.get("output_schema")
                emit_final_chunk = False
                final_json_content = ""

                if self._current_tool_use_partial_json:
                    final_json_content = self._current_tool_use_partial_json
                    try:
                        parsed_input = json.loads(self._current_tool_use_partial_json)
                        if existing_block:
                            # Update existing block from message_start
                            existing_block["input"] = parsed_input
                        else:
                            # New block from content_block_start
                            self._current_tool_use["input"] = parsed_input
                            self._tool_use_blocks.append(self._current_tool_use)
                        emit_final_chunk = output_schema is not None
                    except json.JSONDecodeError:
                        # If JSON parsing fails, only update if we have existing block
                        if existing_block:
                            existing_block["input"] = {}
                        else:
                            self._current_tool_use["input"] = {}
                            self._tool_use_blocks.append(self._current_tool_use)
                        emit_final_chunk = output_schema is not None
                else:
                    # No partial_json - only add if we don't have this block already
                    if not existing_block:
                        self._current_tool_use["input"] = {}
                        self._tool_use_blocks.append(self._current_tool_use)

                # Emit final chunk with complete JSON before clearing
                if emit_final_chunk and final_json_content:
                    chunk = TextGenerationChunk(
                        content=final_json_content,
                        finish_reason=None,
                        usage=None,
                    )
                else:
                    chunk = None

                self._current_tool_use = None
                self._current_tool_use_partial_json = ""

                return chunk
            return None

        # Parse message_start to capture initial content blocks (includes tool_use)
        # Note: In streaming, message_start may contain tool_use blocks with complete input
        # or empty input (which will be filled by content_block_delta events)
        if event_type == "message_start":
            message = event.get("message", {})
            content_blocks = message.get("content", [])
            # Extract tool_use blocks from initial message
            # If input is already populated, use it; otherwise it will be filled by deltas
            for block in content_blocks:
                if block.get("type") == "tool_use":
                    tool_input = block.get("input")
                    # If input is already complete (not empty), use it directly
                    # Otherwise, content_block_start/content_block_stop will fill it
                    if tool_input and isinstance(tool_input, dict) and tool_input:
                        # Complete tool_use block from message_start
                        self._tool_use_blocks.append(
                            {
                                "type": "tool_use",
                                "id": block.get("id"),
                                "name": block.get("name"),
                                "input": tool_input,
                            }
                        )
            return None

        # Parse message delta event for finish reason and usage
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
        """Assemble chunks into final output with structured output support.

        Checks for tool_use blocks first (structured output), then falls back
        to concatenated text chunks.
        """
        # Check if output_schema is provided (tool-based structured output)
        output_schema = self._parameters.get("output_schema")

        if output_schema is not None and self._tool_use_blocks:
            # Extract structured data from tool_use blocks
            # Use the first tool_use block's input
            # For list[BaseModel], tool_input will be wrapped format {"items": [...]}
            # _transform_output will call OutputSchemaMapper.parse_output which handles empty dicts
            tool_input = self._tool_use_blocks[0].get("input")
            # Check if tool_input is valid (not None and not empty dict for BaseModel)
            # Empty dict is OK for list[BaseModel] (converts to []), but invalid for BaseModel
            if tool_input is not None:
                # For BaseModel (not list), empty dict is invalid - try to find text chunks as fallback
                if isinstance(tool_input, dict) and not tool_input:
                    from typing import get_origin

                    origin = get_origin(output_schema)
                    if origin is not list:
                        # Empty dict for BaseModel - try text chunks, but if none, raise error
                        text_content = "".join(chunk.content for chunk in chunks)
                        if text_content:
                            content = self._transform_output(
                                text_content, **self._parameters
                            )
                        else:
                            msg = "Empty tool_use input dict and no text chunks available for BaseModel"
                            raise ValidationError(msg)
                    else:
                        # Empty dict for list[BaseModel] - OK, parse_output will convert to []
                        content = self._transform_output(tool_input, **self._parameters)
                else:
                    # Valid tool_input - transform to BaseModel
                    content = self._transform_output(tool_input, **self._parameters)
            else:
                # Fallback: concatenate text chunks
                text_content = "".join(chunk.content for chunk in chunks)
                if text_content:
                    content = self._transform_output(text_content, **self._parameters)
                else:
                    msg = "No tool_use input and no text chunks available"
                    raise ValidationError(msg)
        else:
            # No tool_use blocks or no output_schema: concatenate text chunks
            content = "".join(chunk.content for chunk in chunks)
            # Apply parameter transformations (e.g., JSON → BaseModel if output_schema provided)
            content = self._transform_output(content, **self._parameters)

        usage = self._parse_usage(chunks)
        finish_reason = chunks[-1].finish_reason if chunks else None

        return TextGenerationOutput(
            content=content,
            usage=usage,
            metadata={"finish_reason": finish_reason},
        )


__all__ = ["AnthropicTextGenerationStream"]
