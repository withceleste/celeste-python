"""OpenAI Responses SSE parsing for streaming."""

from typing import Any

from .client import OpenAIResponsesClient


class OpenAIResponsesStream:
    """Mixin for Responses API SSE parsing.

    Provides shared implementation for all capabilities using OpenAI Responses API streaming:
    - _parse_chunk() - Parse SSE event into raw chunk dict

    Capability streams extend via super() to wrap results in typed Chunks.

    Usage:
        class OpenAITextGenerationStream(OpenAIResponsesStream, TextGenerationStream):
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

        if event_type == "response.output_text.delta":
            delta = event.get("delta")
            if delta is None:
                return None
            return {
                "content": delta,
                "finish_reason": None,
                "usage": None,
                "raw_event": event,
            }

        if event_type == "response.output_text.done":
            return None

        if event_type == "response.completed":
            response_data = event.get("response", {})
            usage_data = response_data.get("usage")

            usage = None
            if usage_data:
                usage = OpenAIResponsesClient.map_usage_fields(usage_data)

            finish_reason = None
            status = response_data.get("status")
            if status == "completed":
                finish_reason = "completed"

            return {
                "content": "",
                "finish_reason": finish_reason,
                "usage": usage,
                "raw_event": event,
            }

        return None


__all__ = ["OpenAIResponsesStream"]
