"""Google Live WebSocket parsing for streaming."""

from typing import Any

from celeste.io import FinishReason

from .client import GoogleLiveClient


def _without_audio(event: dict[str, Any]) -> dict[str, Any]:
    """Copy an event without inline audio payloads."""
    content = event.get("serverContent", {})
    parts = content.get("modelTurn", {}).get("parts")
    if not parts:
        return event
    return {
        **event,
        "serverContent": {
            **content,
            "modelTurn": {
                **content["modelTurn"],
                "parts": [
                    {
                        **part,
                        "inlineData": {
                            k: v for k, v in part["inlineData"].items() if k != "data"
                        },
                    }
                    if "inlineData" in part
                    else part
                    for part in parts
                ],
            },
        },
    }


class GoogleLiveStream:
    """Mixin for Live WebSocket event parsing.

    Provides shared implementation for streaming parsing (provider API level):
    - _parse_chunk_content(event_data) - Extract decoded model audio from an event
    - _parse_chunk_usage(event_data) - Extract and normalize usage from an event
    - _parse_chunk_finish_reason(event_data) - One finish reason per completed model turn

    Modality streams call super() methods which resolve to this via MRO.
    """

    _audio_mime_type: str | None = None
    _interrupted: bool = False

    def _parse_chunk_content(self, event_data: dict[str, Any]) -> bytes | None:
        """Extract decoded model audio, capturing its MIME type once."""
        parts = (
            event_data.get("serverContent", {}).get("modelTurn", {}).get("parts", [])
        )
        audio = [
            part["inlineData"]
            for part in parts
            if isinstance(part.get("inlineData", {}).get("data"), bytes)
            and part["inlineData"].get("mimeType", "").startswith("audio/")
        ]
        if not audio:
            return None
        if self._audio_mime_type is None:
            self._audio_mime_type = audio[0]["mimeType"]
        return b"".join(inline["data"] for inline in audio)

    def _parse_chunk_usage(
        self, event_data: dict[str, Any]
    ) -> dict[str, int | float | None] | None:
        """Extract and normalize usage from an event."""
        usage_data = event_data.get("usageMetadata")
        if usage_data is None:
            return None
        return GoogleLiveClient.map_usage_fields(usage_data)

    def _parse_chunk_finish_reason(
        self, event_data: dict[str, Any]
    ) -> FinishReason | None:
        """Finish on turnComplete unless background thinking continues; label barge-ins."""
        content = event_data.get("serverContent", {})
        if content.get("interrupted"):
            self._interrupted = True
        if not content.get("turnComplete"):
            return None
        status = content.get("interactionStatus", event_data.get("interactionStatus"))
        if status == "IN_PROGRESS":
            return None
        reason = "interrupted" if self._interrupted else "turnComplete"
        self._interrupted = False
        return FinishReason(reason=reason)

    def _build_stream_metadata(
        self, raw_events: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Retain every event without duplicating audio content."""
        return super()._build_stream_metadata(  # type: ignore[misc]
            [_without_audio(event) for event in raw_events]
        )


__all__ = ["GoogleLiveStream"]
