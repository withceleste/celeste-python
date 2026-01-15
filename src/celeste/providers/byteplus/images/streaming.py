"""BytePlus Images SSE parsing for streaming."""

from typing import Any

from celeste.io import FinishReason

from .client import BytePlusImagesClient


class BytePlusImagesStream:
    """Mixin for BytePlus Images API SSE parsing.

    Provides shared implementation for streaming parsing (provider API level):
    - _parse_chunk_content(event_data) - Extract image content from SSE event
    - _parse_chunk_usage(event_data) - Extract and normalize usage from SSE event
    - _parse_chunk_finish_reason(event_data) - Extract finish reason from SSE event
    - _parse_chunk_content_type(event_data) - Get content type ("url" or "b64_json")
    - _parse_chunk_error(event_data) - Get error info for failed events

    Handles all image streaming event types:
    - image_generation.partial_succeeded - Partial image with url or b64_json
    - image_generation.partial_failed - Error event
    - image_generation.completed - Final event with usage only

    Modality streams call super() methods which resolve to this via MRO.
    """

    def _parse_chunk_content(self, event_data: dict[str, Any]) -> str | None:
        """Extract image content from SSE event.

        Returns url or b64_json string if present, None otherwise.
        """
        event_type = event_data.get("type")

        if event_type == "image_generation.partial_succeeded":
            url: str | None = event_data.get("url")
            if url:
                return url
            return event_data.get("b64_json")

        return None

    def _parse_chunk_content_type(self, event_data: dict[str, Any]) -> str | None:
        """Get content type for the event ("url" or "b64_json")."""
        event_type = event_data.get("type")

        if event_type == "image_generation.partial_succeeded":
            if event_data.get("url"):
                return "url"
            if event_data.get("b64_json"):
                return "b64_json"

        return None

    def _parse_chunk_usage(
        self, event_data: dict[str, Any]
    ) -> dict[str, int | float | None] | None:
        """Extract and normalize usage from SSE event."""
        event_type = event_data.get("type")

        if event_type == "image_generation.completed":
            usage_data = event_data.get("usage")
            if usage_data:
                return BytePlusImagesClient.map_usage_fields(usage_data)

        return None

    def _parse_chunk_finish_reason(
        self, event_data: dict[str, Any]
    ) -> FinishReason | None:
        """Extract finish reason from SSE event."""
        event_type = event_data.get("type")

        if event_type == "image_generation.completed":
            return FinishReason(reason="completed")

        return None

    def _parse_chunk_error(self, event_data: dict[str, Any]) -> dict[str, Any] | None:
        """Extract error info from failed events."""
        event_type = event_data.get("type")

        if event_type == "image_generation.partial_failed":
            return event_data.get("error")

        return None

    def _is_error_event(self, event_data: dict[str, Any]) -> bool:
        """Check if this is an error event."""
        return event_data.get("type") == "image_generation.partial_failed"

    def _build_stream_metadata(
        self, raw_events: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Filter content-only events for size efficiency (content is in Output.content)."""
        filtered = [
            e
            for e in raw_events
            if e.get("type") != "image_generation.partial_succeeded"
        ]
        return super()._build_stream_metadata(filtered)  # type: ignore[misc]


__all__ = ["BytePlusImagesStream"]
