"""Google Interactions SSE parsing for streaming."""

import json
from typing import Any, ClassVar

from celeste.io import FinishReason

from .client import GoogleInteractionsClient


def reconstruct_steps(raw_events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rebuild completed steps from step.start/step.delta/step.stop events."""
    pending: dict[int, dict[str, Any]] = {}
    steps: list[dict[str, Any]] = []

    for event in raw_events:
        index = event.get("index")
        if index is None:
            continue

        event_type = event.get("event_type")
        if event_type == "step.start":
            pending[index] = dict(event.get("step") or {})
        elif event_type == "step.delta":
            step = pending.setdefault(index, {})
            delta = event.get("delta") or {}
            delta_type = delta.get("type")
            if delta_type == "text":
                content = step.setdefault("content", [{"type": "text", "text": ""}])
                content[0]["text"] += delta.get("text") or ""
            elif delta_type == "arguments_delta":
                step["_arguments_json"] = step.get("_arguments_json", "") + (
                    delta.get("arguments") or ""
                )
            elif delta_type == "thought_summary":
                summary = step.setdefault("summary", [{"type": "text", "text": ""}])
                summary[0]["text"] += (delta.get("content") or {}).get("text") or ""
            elif delta_type == "thought_signature":
                step["signature"] = step.get("signature", "") + (
                    delta.get("signature") or ""
                )
        elif event_type == "step.stop":
            step = pending.pop(index, None)
            if step is None:
                continue
            raw_arguments = step.pop("_arguments_json", None)
            if raw_arguments is not None:
                step["arguments"] = json.loads(raw_arguments)
            steps.append(step)

    return steps


class GoogleInteractionsStream:
    """Mixin for Interactions SSE parsing.

    Provides shared implementation for streaming parsing (provider API level):
    - _parse_chunk_content(event_data) - Extract content from SSE event
    - _parse_chunk_usage(event_data) - Extract and normalize usage from SSE event
    - _parse_chunk_finish_reason(event_data) - Extract finish reason from SSE event

    Interactions API streaming events are discriminated by `event_type`:
    interaction.created, step.start, step.delta, interaction.status_update,
    interaction.completed, error. Usage and finish status only appear on the
    final interaction.completed event.

    Modality streams call super() methods which resolve to this via MRO.
    """

    _error_type_fields: ClassVar[tuple[str, ...]] = ("code",)

    def _parse_stream_error(self, event_data: dict[str, Any]) -> dict[str, Any] | None:
        """Detect Interactions error events."""
        if event_data.get("event_type") == "error":
            return self._build_error_from_value(event_data.get("error", {}))
        return None

    def _parse_chunk_content(self, event_data: dict[str, Any]) -> str | None:
        """Extract incremental text content from a step.delta event."""
        if event_data.get("event_type") != "step.delta":
            return None
        delta = event_data.get("delta", {})
        if delta.get("type") == "text":
            return delta.get("text") or None
        return None

    def _parse_chunk_reasoning(self, event_data: dict[str, Any]) -> str | None:
        """Extract incremental thought content from a step.delta event."""
        if event_data.get("event_type") != "step.delta":
            return None
        delta = event_data.get("delta", {})
        if delta.get("type") == "thought_summary":
            content = delta.get("content") or {}
            if content.get("type") == "text":
                return content.get("text") or None
        return None

    def _parse_chunk_usage(
        self, event_data: dict[str, Any]
    ) -> dict[str, int | float | None] | None:
        """Extract and normalize usage from the interaction.completed event."""
        if event_data.get("event_type") != "interaction.completed":
            return None
        interaction = event_data.get("interaction") or {}
        usage_data = interaction.get("usage") or event_data.get("usage")
        if usage_data:
            return GoogleInteractionsClient.map_usage_fields(usage_data)
        return None

    def _aggregate_raw_response(
        self, chunks: list[Any], raw_events: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        """Unwrap the final Interaction object from the interaction.completed event."""
        for event in reversed(raw_events):
            event_type = event.get("event_type") or event.get("type")
            if event_type == "interaction.completed":
                interaction = event.get("interaction")
                return interaction if isinstance(interaction, dict) else None
        return None

    def _parse_chunk_finish_reason(
        self, event_data: dict[str, Any]
    ) -> FinishReason | None:
        """Extract finish reason (interaction status) from the completed event."""
        if event_data.get("event_type") != "interaction.completed":
            return None
        interaction = event_data.get("interaction") or {}
        status = interaction.get("status") or event_data.get("status")
        if status:
            return FinishReason(reason=status)
        return None

    def _build_stream_metadata(
        self, raw_events: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Filter content-only events for size efficiency (content is in Output.content)."""
        filtered = [e for e in raw_events if e.get("event_type") != "step.delta"]
        return super()._build_stream_metadata(filtered)  # type: ignore[misc]


__all__ = ["GoogleInteractionsStream", "reconstruct_steps"]
