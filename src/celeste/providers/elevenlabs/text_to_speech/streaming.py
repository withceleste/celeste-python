"""ElevenLabs TextToSpeech streaming parsing."""

from typing import Any


class ElevenLabsTextToSpeechStream:
    """Mixin for TextToSpeech stream parsing.

    Provides shared implementation for streaming parsing (provider API level):
    - _parse_chunk_content(event_data) - Extract audio bytes from event

    ElevenLabs streams raw binary audio, not JSON SSE events.
    The mixin client yields {"data": chunk} for each binary chunk.

    Modality streams call super() methods which resolve to this via MRO.
    """

    def _parse_chunk_content(self, event_data: dict[str, Any]) -> bytes | None:
        """Extract audio bytes from event.

        Returns audio bytes if present, None otherwise.
        """
        return event_data.get("data") or None

    def _build_stream_metadata(
        self, raw_events: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Exclude audio chunks; the binary stream has no metadata events."""
        return super()._build_stream_metadata([])  # type: ignore[misc]


__all__ = ["ElevenLabsTextToSpeechStream"]
