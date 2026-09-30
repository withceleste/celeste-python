"""OpenAI Live WebSocket parsing for streaming."""

from typing import Any

from celeste.io import FinishReason

from .client import OpenAILiveClient


class OpenAILiveStream:
    """Mixin for Live WebSocket event parsing.

    Provides shared implementation for streaming parsing (provider API level):
    - _parse_chunk_content(event_data) - Extract decoded model audio from an event
    - _parse_chunk_usage(event_data) - Extract cumulative usage from an event
    - _parse_chunk_finish_reason(event_data) - The close reason of session.closed

    The primary WebSocket is full duplex: it has no turn or interruption events.

    Modality streams call super() methods which resolve to this via MRO.
    """

    def _parse_stream_error(self, event_data: dict[str, Any]) -> dict[str, Any] | None:
        """Runtime error events leave the session running, so they arrive as chunks."""
        return None

    def _parse_chunk_content(self, event_data: dict[str, Any]) -> bytes | None:
        """Extract decoded model audio from session.output_audio.delta."""
        if event_data.get("type") != "session.output_audio.delta":
            return None
        return event_data.get("delta") or None

    def _parse_chunk_usage(
        self, event_data: dict[str, Any]
    ) -> dict[str, int | float | None] | None:
        """Extract cumulative usage from session.usage.updated or session.closed."""
        if event_data.get("type") not in ("session.usage.updated", "session.closed"):
            return None
        usage_data = event_data.get("usage")
        if usage_data is None:
            return None
        return OpenAILiveClient.map_usage_fields(usage_data)

    def _parse_chunk_finish_reason(
        self, event_data: dict[str, Any]
    ) -> FinishReason | None:
        """Report why the session ended from session.closed."""
        if event_data.get("type") != "session.closed":
            return None
        return FinishReason(reason=event_data.get("reason"))

    def _build_stream_metadata(
        self, raw_events: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Retain every event without duplicating audio content."""
        return super()._build_stream_metadata(  # type: ignore[misc]
            [
                {k: v for k, v in event.items() if k != "delta"}
                if event.get("type") == "session.output_audio.delta"
                else event
                for event in raw_events
            ]
        )


__all__ = ["OpenAILiveStream"]
