"""Ollama Generate NDJSON streaming."""

from typing import Any

from celeste.io import FinishReason

from .client import OllamaGenerateClient


class OllamaGenerateStream:
    """Mixin for Ollama Generate NDJSON parsing.

    Provides shared implementation for streaming parsing (provider API level):
    - _parse_chunk_content(event_data) - Extract image from NDJSON event
    - _parse_chunk_usage(event_data) - Extract usage from NDJSON event
    - _parse_chunk_finish_reason(event_data) - Extract finish reason from NDJSON event
    - _parse_chunk_metadata(event_data) - Extract progress metadata from NDJSON event
    """

    def _parse_chunk_content(self, event_data: dict[str, Any]) -> str | None:
        """Extract base64 image from NDJSON event."""
        return event_data.get("image")

    def _parse_chunk_usage(
        self, event_data: dict[str, Any]
    ) -> dict[str, int | float | None] | None:
        """Extract usage from NDJSON event."""
        if event_data.get("done"):
            return OllamaGenerateClient.map_usage_fields(event_data)
        return None

    def _parse_chunk_finish_reason(
        self, event_data: dict[str, Any]
    ) -> FinishReason | None:
        """Extract finish reason from NDJSON event."""
        if event_data.get("done"):
            return FinishReason(reason="completed")
        return None

    def _parse_chunk_metadata(self, event_data: dict[str, Any]) -> dict[str, Any]:
        """Extract progress metadata from NDJSON event."""
        return {
            "completed": event_data.get("completed"),
            "total": event_data.get("total"),
        }


__all__ = ["OllamaGenerateStream"]
