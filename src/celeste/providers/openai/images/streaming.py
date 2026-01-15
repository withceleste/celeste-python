"""OpenAI Images SSE parsing for streaming."""

from typing import Any

from celeste.io import FinishReason

from .client import OpenAIImagesClient


class OpenAIImagesStream:
    """Mixin for Images API SSE parsing.

    Provides shared implementation for streaming parsing (provider API level):
    - _parse_chunk_content(event_data) - Extract b64_json content from SSE event
    - _parse_chunk_usage(event_data) - Extract and normalize usage from SSE event
    - _parse_chunk_finish_reason(event_data) - Extract finish reason from SSE event
    - _parse_chunk_metadata(event_data) - Extract image metadata from SSE event

    Handles all image streaming event types:
    - image_generation.partial_image / image_generation.completed
    - image_edit.partial_image / image_edit.completed

    Modality streams call super() methods which resolve to this via MRO.
    """

    def _parse_chunk_content(self, event_data: dict[str, Any]) -> str | None:
        """Extract b64_json content from SSE event.

        Returns base64 encoded image string if present, None otherwise.
        """
        event_type = event_data.get("type")
        if not event_type:
            return None

        if event_type in (
            "image_generation.partial_image",
            "image_edit.partial_image",
            "image_generation.completed",
            "image_edit.completed",
        ):
            return event_data.get("b64_json")

        return None

    def _parse_chunk_usage(
        self, event_data: dict[str, Any]
    ) -> dict[str, int | float | None] | None:
        """Extract and normalize usage from SSE event."""
        event_type = event_data.get("type")

        if event_type in ("image_generation.completed", "image_edit.completed"):
            usage_data = event_data.get("usage")
            if usage_data:
                return OpenAIImagesClient.map_usage_fields(usage_data)

        return None

    def _parse_chunk_finish_reason(
        self, event_data: dict[str, Any]
    ) -> FinishReason | None:
        """Extract finish reason from SSE event."""
        event_type = event_data.get("type")

        if event_type in ("image_generation.completed", "image_edit.completed"):
            return FinishReason(reason="completed")

        return None

    def _parse_chunk_metadata(self, event_data: dict[str, Any]) -> dict[str, Any]:
        """Extract image-specific metadata from SSE event."""
        return {
            "size": event_data.get("size"),
            "quality": event_data.get("quality"),
            "output_format": event_data.get("output_format"),
            "background": event_data.get("background"),
            "created_at": event_data.get("created_at"),
            "partial_image_index": event_data.get("partial_image_index"),
        }

    def _build_stream_metadata(
        self, raw_events: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Filter content-only events for size efficiency (content is in Output.content)."""
        filtered = [e for e in raw_events if "partial_image" not in e.get("type", "")]
        return super()._build_stream_metadata(filtered)  # type: ignore[misc]


__all__ = ["OpenAIImagesStream"]
