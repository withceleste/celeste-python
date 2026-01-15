"""Cohere Chat SSE parsing for streaming."""

from typing import Any

from celeste.io import FinishReason

from .client import CohereChatClient


class CohereChatStream:
    """Mixin for Chat API SSE parsing.

    Provides shared implementation for streaming parsing (provider API level):
    - _parse_chunk_content(event_data) - Extract content from SSE event
    - _parse_chunk_usage(event_data) - Extract and normalize usage from SSE event
    - _parse_chunk_finish_reason(event_data) - Extract finish reason from SSE event

    Modality streams call super() methods which resolve to this via MRO.
    """

    def _parse_chunk_content(self, event_data: dict[str, Any]) -> str | None:
        """Extract content from SSE event."""
        event_type = event_data.get("type")

        if event_type == "content-delta":
            delta = event_data.get("delta", {})
            message = delta.get("message", {})
            content = message.get("content", {})
            return content.get("text")

        return None

    def _parse_chunk_usage(
        self, event_data: dict[str, Any]
    ) -> dict[str, int | float | None] | None:
        """Extract and normalize usage from SSE event."""
        event_type = event_data.get("type")

        if event_type == "message-end":
            delta = event_data.get("delta", {})
            usage_dict = delta.get("usage", {})
            if isinstance(usage_dict, dict):
                mapped = CohereChatClient.map_usage_fields(usage_dict)
                if (
                    mapped.get("input_tokens") is not None
                    or mapped.get("output_tokens") is not None
                ):
                    return mapped

        if event_type == "stream-end":
            usage_data = event_data.get("usage", {})
            if isinstance(usage_data, dict):
                mapped = CohereChatClient.map_usage_fields(usage_data)
                if (
                    mapped.get("input_tokens") is not None
                    or mapped.get("output_tokens") is not None
                ):
                    return mapped

        return None

    def _parse_chunk_finish_reason(
        self, event_data: dict[str, Any]
    ) -> FinishReason | None:
        """Extract finish reason from SSE event."""
        event_type = event_data.get("type")

        if event_type == "message-end":
            delta = event_data.get("delta", {})
            finish_reason = delta.get("finish_reason")
            if finish_reason:
                return FinishReason(reason=finish_reason)

        if event_type == "stream-end":
            finish_reason = event_data.get("finish_reason")
            if finish_reason:
                return FinishReason(reason=finish_reason)

        return None

    def _build_stream_metadata(
        self, raw_events: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Filter content-only events for size efficiency (content is in Output.content)."""
        filtered_events = []
        for event in raw_events:
            event_type = event.get("type", "")
            if event_type in {"message-end", "stream-end"}:
                filtered_events.append(event)
        return super()._build_stream_metadata(filtered_events)  # type: ignore[misc]


__all__ = ["CohereChatStream"]
