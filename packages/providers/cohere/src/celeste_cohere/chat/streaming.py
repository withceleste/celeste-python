"""Cohere Chat SSE parsing for streaming."""

from typing import Any

from .client import CohereChatClient


class CohereChatStream:
    """Mixin for Chat API SSE parsing.

    Provides shared implementation for all capabilities using Cohere Chat API streaming:
    - _parse_chunk() - Parse SSE event into raw chunk dict

    Capability streams extend via super() to wrap results in typed Chunks.

    Usage:
        class CohereTextGenerationStream(CohereChatStream, TextGenerationStream):
            def _parse_chunk(self, event):
                raw = super()._parse_chunk(event)
                if not raw:
                    return None
                return TextGenerationChunk(...)
    """

    def _parse_chunk(self, event: dict[str, Any]) -> dict[str, Any] | None:
        """Parse SSE event into raw chunk data."""
        event_type = event.get("type")

        if event_type == "content-delta":
            delta = event.get("delta", {})
            message = delta.get("message", {})
            content = message.get("content", {})
            text_delta = content.get("text")

            if not text_delta:
                return None

            return {
                "content": text_delta,
                "finish_reason": None,
                "usage": None,
                "raw_event": event,
            }

        if event_type == "message-end":
            delta = event.get("delta", {})
            finish_reason = delta.get("finish_reason")

            usage = None
            usage_dict = delta.get("usage", {})
            if isinstance(usage_dict, dict):
                mapped = CohereChatClient.map_usage_fields(usage_dict)
                if (
                    mapped.get("input_tokens") is not None
                    or mapped.get("output_tokens") is not None
                ):
                    usage = mapped

            return {
                "content": "",
                "finish_reason": finish_reason,
                "usage": usage,
                "raw_event": event,
            }

        if event_type == "stream-end":
            finish_reason = event.get("finish_reason")

            usage = None
            usage_data = event.get("usage", {})
            if isinstance(usage_data, dict):
                mapped = CohereChatClient.map_usage_fields(usage_data)
                if (
                    mapped.get("input_tokens") is not None
                    or mapped.get("output_tokens") is not None
                ):
                    usage = mapped

            return {
                "content": "",
                "finish_reason": finish_reason,
                "usage": usage,
                "raw_event": event,
            }

        return None


__all__ = ["CohereChatStream"]
