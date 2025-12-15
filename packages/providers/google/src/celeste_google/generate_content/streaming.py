"""Google GenerateContent SSE parsing for streaming."""

from typing import Any

from .client import GoogleGenerateContentClient


class GoogleGenerateContentStream:
    """Mixin for GenerateContent SSE parsing.

    Provides shared implementation for all capabilities using GenerateContent streaming:
    - _parse_chunk() - Parse SSE event into raw chunk dict

    Capability streams extend via super() to wrap results in typed Chunks.

    Usage:
        class GoogleTextGenerationStream(GoogleGenerateContentStream, TextGenerationStream):
            def _parse_chunk(self, event):
                raw = super()._parse_chunk(event)
                if not raw:
                    return None
                return TextGenerationChunk(...)
    """

    def _parse_chunk(self, event: dict[str, Any]) -> dict[str, Any] | None:
        """Parse SSE event into raw chunk data."""
        candidates = event.get("candidates", [])
        if not candidates:
            return None

        candidate = candidates[0]
        content = candidate.get("content", {})
        parts = content.get("parts", [])

        text_delta = parts[0].get("text") if parts else None
        finish_reason = candidate.get("finishReason")

        usage = None
        usage_data = event.get("usageMetadata")
        if usage_data:
            usage = GoogleGenerateContentClient.map_usage_fields(usage_data)

        if not text_delta and not finish_reason:
            return None

        return {
            "content": text_delta or "",
            "finish_reason": finish_reason,
            "usage": usage,
            "raw_event": event,
        }


__all__ = ["GoogleGenerateContentStream"]
