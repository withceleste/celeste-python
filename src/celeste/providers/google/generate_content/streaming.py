"""Google GenerateContent SSE parsing for streaming."""

from typing import Any, ClassVar

from celeste.io import FinishReason

from .client import GoogleGenerateContentClient


class GoogleGenerateContentStream:
    """Mixin for GenerateContent SSE parsing.

    Provides shared implementation for streaming parsing (provider API level):
    - _parse_chunk_content(event_data) - Extract content from SSE event
    - _parse_chunk_usage(event_data) - Extract and normalize usage from SSE event
    - _parse_chunk_finish_reason(event_data) - Extract finish reason from SSE event

    Modality streams call super() methods which resolve to this via MRO.
    """

    _error_type_fields: ClassVar[tuple[str, ...]] = ("status", "code")
    _content_parts: list[dict[str, Any]]
    _grounding_part_fragments: list[list[dict[str, Any]]]
    _grounding_metadata: list[dict[str, Any]]

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        super().__init__(*args, **kwargs)
        self._content_parts = []
        self._grounding_part_fragments = []
        self._grounding_metadata = []

    def _parse_chunk(self, event_data: dict[str, Any]) -> Any | None:  # noqa: ANN401
        """Capture native Parts and grounding before normal chunk filtering."""
        candidates = event_data.get("candidates", [])
        if candidates:
            candidate = candidates[0]
            parts = candidate.get("content", {}).get("parts", [])
            self._content_parts.extend(parts)
            # Treat adjacent SSE text as a continuation; keep in-event Parts distinct.
            if (
                self._grounding_part_fragments
                and parts
                and isinstance(self._grounding_part_fragments[-1][-1].get("text"), str)
                and isinstance(parts[0].get("text"), str)
                and bool(self._grounding_part_fragments[-1][-1].get("thought"))
                == bool(parts[0].get("thought"))
            ):
                self._grounding_part_fragments[-1].append(parts[0])
                parts = parts[1:]
            self._grounding_part_fragments.extend([part] for part in parts)
            meta = candidate.get("groundingMetadata")
            if isinstance(meta, dict):
                self._grounding_metadata.append(meta)
        return super()._parse_chunk(event_data)  # type: ignore[misc]

    def _parse_chunk_content(self, event_data: dict[str, Any]) -> str | None:
        """Join non-thought text from every Part of the first candidate."""
        candidates = event_data.get("candidates", [])
        if not candidates:
            return None

        candidate = candidates[0]
        content = candidate.get("content", {})
        parts = content.get("parts", [])

        texts = [
            part["text"]
            for part in parts
            if not part.get("thought") and part.get("text") is not None
        ]
        return "".join(texts) if texts else None

    def _parse_chunk_reasoning(self, event_data: dict[str, Any]) -> str | None:
        """Extract thought content from SSE event."""
        candidates = event_data.get("candidates", [])
        if not candidates:
            return None

        parts = candidates[0].get("content", {}).get("parts", [])
        return (
            "".join(p["text"] for p in parts if p.get("thought") and p.get("text"))
            or None
        )

    def _parse_chunk_usage(
        self, event_data: dict[str, Any]
    ) -> dict[str, int | float | None] | None:
        """Extract and normalize usage from SSE event."""
        usage_data = event_data.get("usageMetadata")
        if usage_data:
            return GoogleGenerateContentClient.map_usage_fields(usage_data)

        return None

    def _aggregate_raw_response(
        self, chunks: list[Any], raw_events: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        """The last chunk carrying cumulative usageMetadata is response-shaped."""
        for event in reversed(raw_events):
            if isinstance(event.get("usageMetadata"), dict):
                return event
        return None

    def _parse_chunk_finish_reason(
        self, event_data: dict[str, Any]
    ) -> FinishReason | None:
        """Extract finish reason from SSE event."""
        candidates = event_data.get("candidates", [])
        if not candidates:
            return None

        candidate = candidates[0]
        finish_reason = candidate.get("finishReason")
        if finish_reason:
            return FinishReason(reason=finish_reason)

        return None

    def _build_stream_metadata(
        self, raw_events: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Filter content-only events for size efficiency (content is in Output.content)."""
        filtered = [e for e in raw_events if e.get("usageMetadata")]
        return super()._build_stream_metadata(filtered)  # type: ignore[misc]


__all__ = ["GoogleGenerateContentStream"]
