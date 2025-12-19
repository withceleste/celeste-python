"""BytePlus Images SSE parsing for streaming."""

from typing import Any

from .client import BytePlusImagesClient


class BytePlusImagesStream:
    """Mixin for BytePlus Images API SSE parsing.

    Provides shared implementation for capabilities using BytePlus Images API streaming:
    - _parse_chunk() - Parse SSE event into raw chunk dict

    Handles all image streaming event types:
    - image_generation.partial_succeeded - Partial image with url or b64_json
    - image_generation.partial_failed - Error event
    - image_generation.completed - Final event with usage only

    Capability streams extend via super() to wrap results in typed Chunks.

    Usage:
        class BytePlusImageGenerationStream(BytePlusImagesStream, ImageGenerationStream):
            def _parse_chunk(self, event):
                raw = super()._parse_chunk(event)
                if not raw:
                    return None
                return ImageGenerationChunk(...)
    """

    def _parse_chunk(self, event: dict[str, Any]) -> dict[str, Any] | None:
        """Parse SSE event into raw chunk data.

        Returns dict with:
        - content_type: "url" or "b64_json" or None
        - content: url string or b64_json string
        - is_error: True for partial_failed events
        - error: error dict for failed events
        - usage: usage dict from completed event (None otherwise)
        - metadata: model, created, image_index, size
        - raw_event: original event dict
        """
        event_type = event.get("type")
        if not event_type:
            return None

        # Handle successful partial image
        if event_type == "image_generation.partial_succeeded":
            url = event.get("url")
            b64_json = event.get("b64_json")

            content_type = None
            content = None
            if url:
                content_type = "url"
                content = url
            elif b64_json:
                content_type = "b64_json"
                content = b64_json

            if not content:
                return None

            return {
                "content_type": content_type,
                "content": content,
                "is_error": False,
                "error": None,
                "usage": None,
                "metadata": {
                    "model": event.get("model"),
                    "created": event.get("created"),
                    "image_index": event.get("image_index"),
                    "size": event.get("size"),
                },
                "raw_event": event,
            }

        # Handle failed partial image
        if event_type == "image_generation.partial_failed":
            return {
                "content_type": None,
                "content": None,
                "is_error": True,
                "error": event.get("error"),
                "usage": None,
                "metadata": {
                    "model": event.get("model"),
                    "created": event.get("created"),
                    "image_index": event.get("image_index"),
                },
                "raw_event": event,
            }

        # Handle completed event (usage only, no image)
        if event_type == "image_generation.completed":
            usage_data = event.get("usage")
            usage = None
            if usage_data:
                usage = BytePlusImagesClient.map_usage_fields(usage_data)
            return {
                "content_type": None,
                "content": None,
                "is_error": False,
                "error": None,
                "usage": usage,
                "metadata": {
                    "model": event.get("model"),
                    "created": event.get("created"),
                },
                "raw_event": event,
            }

        return None


__all__ = ["BytePlusImagesStream"]
