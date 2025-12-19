"""OpenAI Images SSE parsing for streaming."""

from typing import Any

from .client import OpenAIImagesClient


class OpenAIImagesStream:
    """Mixin for Images API SSE parsing.

    Provides shared implementation for capabilities using OpenAI Images API streaming:
    - _parse_chunk() - Parse SSE event into raw chunk dict

    Handles all image streaming event types:
    - image_generation.partial_image / image_generation.completed
    - image_edit.partial_image / image_edit.completed

    Capability streams extend via super() to wrap results in typed Chunks.

    Usage:
        class OpenAIImageGenerationStream(OpenAIImagesStream, ImageGenerationStream):
            def _parse_chunk(self, event):
                raw = super()._parse_chunk(event)
                if not raw:
                    return None
                return ImageGenerationChunk(...)
    """

    def _parse_chunk(self, event: dict[str, Any]) -> dict[str, Any] | None:
        """Parse SSE event into raw chunk data.

        Returns dict with:
        - content: b64_json string (raw, not decoded)
        - is_partial: True for partial_image events, False for completed
        - usage: usage dict from completed events (None for partials)
        - metadata: size, quality, output_format, background, created_at, partial_image_index
        - raw_event: original event dict
        """
        event_type = event.get("type")
        if not event_type:
            return None

        # Handle partial image events (generation or edit)
        if event_type in ("image_generation.partial_image", "image_edit.partial_image"):
            b64_json = event.get("b64_json")
            if not b64_json:
                return None
            return {
                "content": b64_json,
                "is_partial": True,
                "usage": None,
                "metadata": {
                    "size": event.get("size"),
                    "quality": event.get("quality"),
                    "output_format": event.get("output_format"),
                    "background": event.get("background"),
                    "created_at": event.get("created_at"),
                    "partial_image_index": event.get("partial_image_index"),
                },
                "raw_event": event,
            }

        # Handle completed events (generation or edit)
        if event_type in ("image_generation.completed", "image_edit.completed"):
            b64_json = event.get("b64_json")
            if not b64_json:
                return None
            usage_data = event.get("usage")
            usage = None
            if usage_data:
                usage = OpenAIImagesClient.map_usage_fields(usage_data)
            return {
                "content": b64_json,
                "is_partial": False,
                "usage": usage,
                "metadata": {
                    "size": event.get("size"),
                    "quality": event.get("quality"),
                    "output_format": event.get("output_format"),
                    "background": event.get("background"),
                    "created_at": event.get("created_at"),
                },
                "raw_event": event,
            }

        return None


__all__ = ["OpenAIImagesStream"]
