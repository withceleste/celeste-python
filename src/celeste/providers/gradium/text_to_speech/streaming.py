"""Gradium TextToSpeech WebSocket parsing for streaming."""

from typing import Any

from celeste.io import FinishReason


class GradiumTextToSpeechStream:
    """Mixin for TextToSpeech WebSocket stream parsing.

    Provides shared implementation for streaming parsing (provider API level):
    - _parse_chunk_content(event_data) - Extract audio bytes from WebSocket event
    - _parse_chunk_usage(event_data) - Extract and normalize usage from event
    - _parse_chunk_finish_reason(event_data) - Extract finish reason from event

    Gradium TTS streams audio via WebSocket, yielding {"data": bytes} events.

    Modality streams call super() methods which resolve to this via MRO.
    """

    def _parse_chunk_content(self, event_data: dict[str, Any]) -> bytes | None:
        """Extract audio bytes from event.

        Returns audio bytes if present, None otherwise.
        """
        return event_data.get("data")

    def _parse_chunk_usage(
        self, event_data: dict[str, Any]
    ) -> dict[str, int | float | None] | None:
        """Extract and normalize usage from event.

        Gradium TTS doesn't return usage in stream.
        """
        return None

    def _parse_chunk_finish_reason(
        self, event_data: dict[str, Any]
    ) -> FinishReason | None:
        """Extract finish reason from WebSocket event.

        Returns FinishReason if end_of_stream received.
        """
        finish_reason = event_data.get("finish_reason")
        if finish_reason:
            return FinishReason(reason=finish_reason)
        return None

    def _build_stream_metadata(
        self, raw_events: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Filter to keep only metadata events.

        Gradium WebSocket stream has no metadata events.
        """
        return super()._build_stream_metadata(raw_events)  # type: ignore[misc]


__all__ = ["GradiumTextToSpeechStream"]
