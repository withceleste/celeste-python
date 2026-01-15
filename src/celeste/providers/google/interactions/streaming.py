"""Google Interactions SSE parsing for streaming."""

from typing import Any

from celeste.io import FinishReason

from .client import GoogleInteractionsClient


class GoogleInteractionsStream:
    """Mixin for Interactions SSE parsing.

    Provides shared implementation for streaming parsing (provider API level):
    - _parse_chunk_content(event_data) - Extract content from SSE event
    - _parse_chunk_usage(event_data) - Extract and normalize usage from SSE event
    - _parse_chunk_finish_reason(event_data) - Extract finish reason from SSE event

    Interactions API streaming uses different event types than GenerateContent:
    - content.delta: Incremental content updates
    - interaction.complete: Final interaction data with usage

    Modality streams call super() methods which resolve to this via MRO.
    """

    def _parse_chunk_content(self, event_data: dict[str, Any]) -> str | None:
        """Extract content from SSE event.

        Returns content string if present, None otherwise.
        """
        event_type = event_data.get("event_type") or event_data.get("type")

        # Handle content delta events
        if event_type == "content.delta":
            delta = event_data.get("delta", {})
            delta_type = delta.get("type")

            if delta_type == "text":
                return delta.get("text", "")
            # Note: thought deltas are not returned as content (modality-specific handling)

        # Handle interaction complete events
        if event_type == "interaction.complete":
            interaction = event_data.get("interaction", {})
            outputs = interaction.get("outputs", [])

            # Extract text from outputs
            text_content = ""
            for output in outputs:
                output_type = output.get("type")
                if output_type == "text":
                    text_content += output.get("text", "")
            if text_content:
                return text_content

        return None

    def _parse_chunk_usage(
        self, event_data: dict[str, Any]
    ) -> dict[str, int | float | None] | None:
        """Extract and normalize usage from SSE event.

        Returns normalized usage dict if present, None otherwise.
        """
        event_type = event_data.get("event_type") or event_data.get("type")

        # Handle interaction complete events
        if event_type == "interaction.complete":
            interaction = event_data.get("interaction", {})
            usage_data = interaction.get("usage")
            if usage_data:
                return GoogleInteractionsClient.map_usage_fields(usage_data)

        return None

    def _parse_chunk_finish_reason(
        self, event_data: dict[str, Any]
    ) -> FinishReason | None:
        """Extract finish reason from SSE event.

        Returns FinishReason if present, None otherwise.
        """
        event_type = event_data.get("event_type") or event_data.get("type")

        # Handle interaction complete events
        if event_type == "interaction.complete":
            interaction = event_data.get("interaction", {})
            outputs = interaction.get("outputs", [])

            # Check for finish_reason in various locations
            finish_reason = interaction.get("finish_reason")
            if not finish_reason and outputs:
                finish_reason = outputs[-1].get("finish_reason")
            if finish_reason:
                return FinishReason(reason=finish_reason)

        return None

    def _build_stream_metadata(
        self, raw_events: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Filter content-only events for size efficiency (content is in Output.content)."""
        filtered = [
            e
            for e in raw_events
            if (e.get("type", "") or e.get("event_type", "")) != "content.delta"
        ]
        return super()._build_stream_metadata(filtered)  # type: ignore[misc]


__all__ = ["GoogleInteractionsStream"]
