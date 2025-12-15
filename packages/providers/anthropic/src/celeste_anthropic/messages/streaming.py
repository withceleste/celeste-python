"""Anthropic Messages SSE parsing for streaming."""

from typing import Any

from .client import AnthropicMessagesClient


class AnthropicMessagesStream:
    """Mixin for Messages API SSE parsing.

    Provides shared implementation for all capabilities using Anthropic Messages API streaming:
    - _parse_chunk() - Parse SSE event into raw chunk dict

    Capability streams extend via super() to wrap results in typed Chunks.

    Usage:
        class AnthropicTextGenerationStream(AnthropicMessagesStream, TextGenerationStream):
            def _parse_chunk(self, event):
                raw = super()._parse_chunk(event)
                if not raw:
                    return None
                return TextGenerationChunk(...)
    """

    def _parse_chunk(self, event: dict[str, Any]) -> dict[str, Any] | None:
        """Parse SSE event into raw chunk data."""
        event_type = event.get("type")
        if not event_type:
            return None

        if event_type == "content_block_delta":
            delta = event.get("delta", {})
            if delta.get("type") == "text_delta":
                text_delta = delta.get("text")
                if text_delta is not None:
                    return {
                        "content": text_delta,
                        "finish_reason": None,
                        "usage": None,
                        "raw_event": event,
                    }
            return None

        if event_type == "message_delta":
            delta = event.get("delta", {})
            stop_reason = delta.get("stop_reason")

            usage = None
            usage_data = event.get("usage")
            if usage_data:
                usage = AnthropicMessagesClient.map_usage_fields(usage_data)

            return {
                "content": "",
                "finish_reason": stop_reason,
                "usage": usage,
                "raw_event": event,
            }

        if event_type == "message_stop":
            usage = None
            usage_data = event.get("usage")
            if usage_data:
                usage = AnthropicMessagesClient.map_usage_fields(usage_data)

            return {
                "content": "",
                "finish_reason": None,
                "usage": usage,
                "raw_event": event,
            }

        return None


__all__ = ["AnthropicMessagesStream"]
