"""Anthropic Messages SSE parsing for streaming."""

from typing import Any

from celeste.io import FinishReason

from .client import AnthropicMessagesClient


class AnthropicMessagesStream:
    """Mixin for Messages API SSE parsing.

    Provides shared implementation for streaming parsing (provider API level):
    - _parse_chunk_content(event_data) - Extract content from SSE event
    - _parse_chunk_usage(event_data) - Extract and normalize usage from SSE event
    - _parse_chunk_finish_reason(event_data) - Extract finish reason from SSE event

    Modality streams call super() methods which resolve to this via MRO.
    """

    def _parse_chunk_content(self, event_data: dict[str, Any]) -> str | None:
        """Extract content from SSE event.

        Returns content string if present, None otherwise.
        """
        event_type = event_data.get("type")

        if event_type == "content_block_delta":
            delta = event_data.get("delta", {})
            if delta.get("type") == "text_delta":
                return delta.get("text")

        return None

    def _parse_chunk_usage(
        self, event_data: dict[str, Any]
    ) -> dict[str, int | float | None] | None:
        """Extract and normalize usage from SSE event.

        Returns normalized usage dict if present, None otherwise.
        """
        event_type = event_data.get("type")

        if event_type in ("message_delta", "message_stop"):
            usage_data = event_data.get("usage")
            if usage_data:
                return AnthropicMessagesClient.map_usage_fields(usage_data)

        return None

    def _parse_chunk_finish_reason(
        self, event_data: dict[str, Any]
    ) -> FinishReason | None:
        """Extract finish reason from SSE event.

        Returns FinishReason if present, None otherwise.
        """
        event_type = event_data.get("type")

        if event_type == "message_delta":
            delta = event_data.get("delta", {})
            stop_reason = delta.get("stop_reason")
            if stop_reason:
                return FinishReason(reason=stop_reason)

        return None

    def _build_stream_metadata(
        self, raw_events: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Filter content-only events for size efficiency (content is in Output.content)."""
        filtered = [e for e in raw_events if e.get("type") != "content_block_delta"]
        return super()._build_stream_metadata(filtered)  # type: ignore[misc]


__all__ = ["AnthropicMessagesStream"]
