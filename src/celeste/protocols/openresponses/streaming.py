"""OpenResponses protocol SSE parsing for streaming."""

from typing import Any, ClassVar

from celeste.io import FinishReason

from .client import OpenResponsesClient


class OpenResponsesStream:
    """OpenResponses protocol SSE parsing mixin.

    Provides shared implementation for streaming parsing (protocol level):
    - _parse_chunk_content(event_data) - Extract content from SSE event
    - _parse_chunk_usage(event_data) - Extract and normalize usage from SSE event
    - _parse_chunk_finish_reason(event_data) - Extract finish reason from SSE event
    - _build_stream_metadata(raw_events) - Filter content-only events

    Provider streams inherit this and override methods for provider-specific behavior
    (e.g., thinking model content parsing, non-standard usage locations).

    Modality streams call super() methods which resolve to this via MRO.
    """

    _error_type_fields: ClassVar[tuple[str, ...]] = ("code",)

    def _parse_stream_error(self, event_data: dict[str, Any]) -> dict[str, Any] | None:
        """Detect Responses API error events (flat shape: code/message at root level)."""
        if event_data.get("type") == "error":
            return self._build_error_from_value(event_data)  # type: ignore[attr-defined, no-any-return]
        return None

    def _parse_chunk_content(self, event_data: dict[str, Any]) -> str | None:
        """Extract content from SSE event."""
        event_type = event_data.get("type")
        if event_type == "response.output_text.delta":
            return event_data.get("delta") or None
        return None

    def _parse_chunk_usage(
        self, event_data: dict[str, Any]
    ) -> dict[str, int | float | None] | None:
        """Extract and normalize usage from SSE event."""
        event_type = event_data.get("type")
        if event_type == "response.completed":
            response_data = event_data.get("response", {})
            usage_data = response_data.get("usage")
            if usage_data:
                return OpenResponsesClient.map_usage_fields(usage_data)
        return None

    def _parse_chunk_finish_reason(
        self, event_data: dict[str, Any]
    ) -> FinishReason | None:
        """Extract finish reason from SSE event."""
        event_type = event_data.get("type")
        if event_type == "response.completed":
            response_data = event_data.get("response", {})
            status = response_data.get("status")
            if status == "completed":
                return FinishReason(reason="completed")
        return None

    def _build_stream_metadata(
        self, raw_events: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Filter content-only events for size efficiency."""
        filtered = [
            e
            for e in raw_events
            if "delta" not in e.get("type", "")
            and e.get("type") != "response.completed"
        ]
        return super()._build_stream_metadata(filtered)  # type: ignore[misc, no-any-return]


__all__ = ["OpenResponsesStream"]
