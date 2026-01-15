"""Mistral Chat SSE parsing for streaming."""

from typing import Any

from celeste.io import FinishReason

from .client import MistralChatClient


class MistralChatStream:
    """Mixin for Chat API SSE parsing.

    Provides shared implementation for streaming parsing (provider API level):
    - _parse_chunk_content(event_data) - Extract content from SSE event
    - _parse_chunk_usage(event_data) - Extract and normalize usage from SSE event
    - _parse_chunk_finish_reason(event_data) - Extract finish reason from SSE event

    Modality streams call super() methods which resolve to this via MRO.
    """

    def _parse_chunk_content(self, event_data: dict[str, Any]) -> str | None:
        """Extract content from SSE event."""
        choices = event_data.get("choices", [])
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
            return "".join(text_parts) if text_parts else None

        return content_delta

    def _parse_chunk_usage(
        self, event_data: dict[str, Any]
    ) -> dict[str, int | float | None] | None:
        """Extract and normalize usage from SSE event."""
        usage_data = event_data.get("usage")
        if isinstance(usage_data, dict):
            return MistralChatClient.map_usage_fields(usage_data)

        return None

    def _parse_chunk_finish_reason(
        self, event_data: dict[str, Any]
    ) -> FinishReason | None:
        """Extract finish reason from SSE event."""
        choices = event_data.get("choices", [])
        if not choices:
            return None

        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            return None

        finish_reason = first_choice.get("finish_reason")
        if finish_reason:
            return FinishReason(reason=finish_reason)

        return None

    def _build_stream_metadata(
        self, raw_events: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Filter content-only events for size efficiency (content is in Output.content)."""
        filtered = [event for event in raw_events if event.get("usage")]
        return super()._build_stream_metadata(filtered)  # type: ignore[misc]


__all__ = ["MistralChatStream"]
