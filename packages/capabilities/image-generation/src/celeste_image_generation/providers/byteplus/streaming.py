"""BytePlus streaming for image generation."""

import base64
import logging
from collections.abc import AsyncIterator
from typing import Any

from celeste_byteplus.images.streaming import BytePlusImagesStream

from celeste.artifacts import ImageArtifact
from celeste.core import UsageField
from celeste.mime_types import ImageMimeType
from celeste_image_generation.io import ImageGenerationChunk, ImageGenerationUsage
from celeste_image_generation.streaming import ImageGenerationStream

logger = logging.getLogger(__name__)


class BytePlusImageGenerationStream(BytePlusImagesStream, ImageGenerationStream):
    """BytePlus streaming for image generation."""

    def __init__(self, sse_iterator: AsyncIterator[dict[str, Any]]) -> None:
        """Initialize stream and track completed event usage."""
        super().__init__(sse_iterator)
        self._completed_usage: ImageGenerationUsage | None = None

    def _parse_chunk(self, chunk_data: dict[str, Any]) -> ImageGenerationChunk | None:
        """Parse chunk from SSE event.

        Uses provider mixin to parse raw SSE event, then wraps in typed chunk.
        """
        raw = super()._parse_chunk(chunk_data)
        if not raw:
            return None

        # Handle error events
        if raw.get("is_error"):
            error = raw.get("error", {})
            logger.error(
                "Image generation failed: %s - %s",
                error.get("code"),
                error.get("message"),
            )
            return None

        # Handle completed event (usage only)
        usage_data = raw.get("usage")
        if usage_data:
            self._completed_usage = ImageGenerationUsage(
                total_tokens=usage_data.get(UsageField.TOTAL_TOKENS),
                output_tokens=usage_data.get(UsageField.OUTPUT_TOKENS),
                num_images=usage_data.get(UsageField.NUM_IMAGES),
            )
            return None

        # Handle partial succeeded (image content)
        content = raw.get("content")
        content_type = raw.get("content_type")
        if not content:
            return None

        if content_type == "url":
            artifact = ImageArtifact(url=content, mime_type=ImageMimeType.PNG)
        else:  # b64_json
            image_data = base64.b64decode(content)
            artifact = ImageArtifact(data=image_data)

        return ImageGenerationChunk(content=artifact)

    def _parse_usage(self, chunks: list[ImageGenerationChunk]) -> ImageGenerationUsage:
        """Parse usage from chunks.

        Usage is stored from the completed event.
        """
        if self._completed_usage is not None:
            return self._completed_usage

        return ImageGenerationUsage()


__all__ = ["BytePlusImageGenerationStream"]
