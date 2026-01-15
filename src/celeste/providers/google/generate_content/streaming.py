"""Google GenerateContent SSE parsing for streaming."""

from typing import Any

from celeste.io import FinishReason

from .client import GoogleGenerateContentClient


class GoogleGenerateContentStream:
    """Mixin for GenerateContent SSE parsing.

    Provides shared implementation for streaming parsing (provider API level):
    - _parse_chunk_content(event_data) - Extract content from SSE event
    - _parse_chunk_usage(event_data) - Extract and normalize usage from SSE event
    - _parse_chunk_finish_reason(event_data) - Extract finish reason from SSE event

    Modality streams call super() methods which resolve to this via MRO.
    """

    def _parse_chunk_content(self, event_data: dict[str, Any]) -> str | None:
        """Extract content from SSE event."""
        candidates = event_data.get("candidates", [])
        if not candidates:
            return None

        candidate = candidates[0]
        content = candidate.get("content", {})
        parts = content.get("parts", [])

        if parts:
            return parts[0].get("text")

        return None

    def _parse_chunk_usage(
        self, event_data: dict[str, Any]
    ) -> dict[str, int | float | None] | None:
        """Extract and normalize usage from SSE event."""
        usage_data = event_data.get("usageMetadata")
        if usage_data:
            return GoogleGenerateContentClient.map_usage_fields(usage_data)

        return None

    def _parse_chunk_finish_reason(
        self, event_data: dict[str, Any]
    ) -> FinishReason | None:
        """Extract finish reason from SSE event."""
        candidates = event_data.get("candidates", [])
        if not candidates:
            return None

        candidate = candidates[0]
        finish_reason = candidate.get("finishReason")
        if finish_reason:
            return FinishReason(reason=finish_reason)

        return None

    def _build_stream_metadata(
        self, raw_events: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Filter content-only events for size efficiency (content is in Output.content)."""
        filtered = [e for e in raw_events if e.get("usageMetadata")]
        return super()._build_stream_metadata(filtered)  # type: ignore[misc]


__all__ = ["GoogleGenerateContentStream"]
