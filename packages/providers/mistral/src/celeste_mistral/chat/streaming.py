"""Mistral Chat SSE parsing for streaming."""

from typing import Any

from .client import MistralChatClient


class MistralChatStream:
    """Mixin for Chat API SSE parsing.

    Provides shared implementation for all capabilities using Mistral Chat API streaming:
    - _parse_chunk() - Parse SSE event into raw chunk dict

    Capability streams extend via super() to wrap results in typed Chunks.

    Usage:
        class MistralTextGenerationStream(MistralChatStream, TextGenerationStream):
            def _parse_chunk(self, event):
                raw = super()._parse_chunk(event)
                if not raw:
                    return None
                return TextGenerationChunk(...)
    """

    def _parse_chunk(self, event: dict[str, Any]) -> dict[str, Any] | None:
        """Parse SSE event into raw chunk data."""
        choices = event.get("choices", [])
        if not choices:
            return None

        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            return None

        delta = first_choice.get("delta", {})
        if not isinstance(delta, dict):
            return None

        content_delta = delta.get("content")

        # Handle magistral thinking models that may return list content
        if isinstance(content_delta, list):
            text_parts = []
            for block in content_delta:
                if isinstance(block, dict) and block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
            content_delta = "".join(text_parts) if text_parts else None

        finish_reason = first_choice.get("finish_reason")

        usage = None
        usage_data = event.get("usage")
        if isinstance(usage_data, dict):
            usage = MistralChatClient.map_usage_fields(usage_data)

        if not content_delta and not finish_reason:
            return None

        return {
            "content": content_delta or "",
            "finish_reason": finish_reason,
            "usage": usage,
            "raw_event": event,
        }


__all__ = ["MistralChatStream"]
