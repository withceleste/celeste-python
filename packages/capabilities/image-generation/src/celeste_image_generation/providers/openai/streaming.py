"""OpenAI streaming for image generation."""

import base64
import logging
from typing import Any

from celeste_openai.images.streaming import OpenAIImagesStream

from celeste.artifacts import ImageArtifact
from celeste.core import UsageField
from celeste_image_generation.io import ImageGenerationChunk, ImageGenerationUsage
from celeste_image_generation.streaming import ImageGenerationStream

logger = logging.getLogger(__name__)


class OpenAIImageGenerationStream(OpenAIImagesStream, ImageGenerationStream):
    """OpenAI streaming for image generation."""

    def _parse_chunk(self, chunk_data: dict[str, Any]) -> ImageGenerationChunk | None:
        """Parse chunk from SSE event.

        Uses provider mixin to parse raw SSE event, then wraps in typed chunk.
        """
        raw = super()._parse_chunk(chunk_data)
        if not raw:
            return None

        b64_json = raw.get("content")
        if not b64_json:
            return None

        image_data = base64.b64decode(b64_json)
        artifact = ImageArtifact(data=image_data)

        # Parse usage from raw dict (already mapped to UsageField keys)
        usage = None
        usage_data = raw.get("usage")
        if usage_data:
            usage = ImageGenerationUsage(
                total_tokens=usage_data.get(UsageField.TOTAL_TOKENS),
                input_tokens=usage_data.get(UsageField.INPUT_TOKENS),
                output_tokens=usage_data.get(UsageField.OUTPUT_TOKENS),
            )

        return ImageGenerationChunk(content=artifact, usage=usage)

    def _parse_usage(self, chunks: list[ImageGenerationChunk]) -> ImageGenerationUsage:
        """Parse usage from chunks.

        Usage is only available in the final completed event.
        """
        for chunk in reversed(chunks):
            if chunk.usage is not None:
                return chunk.usage

        return ImageGenerationUsage()


__all__ = ["OpenAIImageGenerationStream"]
