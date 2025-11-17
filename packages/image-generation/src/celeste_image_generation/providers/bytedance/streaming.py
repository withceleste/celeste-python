"""ByteDance streaming for image generation."""

import logging
from collections.abc import AsyncIterator
from typing import Any

from celeste.artifacts import ImageArtifact
from celeste.mime_types import ImageMimeType
from celeste_image_generation.io import ImageGenerationChunk, ImageGenerationUsage
from celeste_image_generation.streaming import ImageGenerationStream

logger = logging.getLogger(__name__)


class ByteDanceImageGenerationStream(ImageGenerationStream):
    """ByteDance streaming for image generation."""

    def __init__(self, sse_iterator: AsyncIterator[dict[str, Any]]) -> None:
        """Initialize stream and track completed event usage."""
        super().__init__(sse_iterator)
        self._completed_usage: ImageGenerationUsage | None = None

    def _parse_chunk(self, chunk_data: dict[str, Any]) -> ImageGenerationChunk | None:
        """Parse chunk from SSE event."""
        event_type = chunk_data.get("type")

        if event_type == "image_generation.partial_succeeded":
            url = chunk_data.get("url")
            if not url:
                logger.warning("partial_succeeded event missing URL")
                return None

            artifact = ImageArtifact(url=url, mime_type=ImageMimeType.PNG)
            return ImageGenerationChunk(content=artifact)

        if event_type == "image_generation.completed":
            usage_data = chunk_data.get("usage")
            if usage_data:
                self._completed_usage = ImageGenerationUsage(
                    total_tokens=usage_data.get("total_tokens"),
                    input_tokens=None,
                    output_tokens=None,
                )
            return None

        if event_type == "image_generation.partial_failed":
            error = chunk_data.get("error", {})
            logger.error(
                "Image generation failed: %s - %s",
                error.get("code"),
                error.get("message"),
            )
            return None

        logger.warning("Unknown event type: %s", event_type)
        return None

    def _parse_usage(self, chunks: list[ImageGenerationChunk]) -> ImageGenerationUsage:
        """Parse usage from chunks."""
        if self._completed_usage is not None:
            return self._completed_usage

        return ImageGenerationUsage()


__all__ = ["ByteDanceImageGenerationStream"]
