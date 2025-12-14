"""OpenAI streaming for image generation."""

import base64
import logging
from typing import Any

from celeste.artifacts import ImageArtifact
from celeste_image_generation.io import ImageGenerationChunk, ImageGenerationUsage
from celeste_image_generation.streaming import ImageGenerationStream

logger = logging.getLogger(__name__)


class OpenAIImageGenerationStream(ImageGenerationStream):
    """OpenAI streaming for image generation."""

    def _parse_chunk(self, chunk_data: dict[str, Any]) -> ImageGenerationChunk | None:
        """Parse chunk from SSE event.

        OpenAI returns two event types:
        - image_generation.partial_image: Progressive image chunks
        - image_generation.completed: Final image with usage data
        """
        event_type = chunk_data.get("type")

        if event_type == "image_generation.partial_image":
            # Partial image chunk
            b64_json = chunk_data.get("b64_json")
            if not b64_json:
                return None

            image_data = base64.b64decode(b64_json)
            artifact = ImageArtifact(data=image_data)

            return ImageGenerationChunk(content=artifact)

        if event_type == "image_generation.completed":
            # Final image with usage
            b64_json = chunk_data.get("b64_json")
            if not b64_json:
                return None

            image_data = base64.b64decode(b64_json)
            artifact = ImageArtifact(data=image_data)

            # Parse usage from completed event
            usage_data = chunk_data.get("usage")
            usage = None
            if usage_data:
                usage = ImageGenerationUsage(
                    total_tokens=usage_data.get("total_tokens"),
                    input_tokens=usage_data.get("input_tokens"),
                    output_tokens=usage_data.get("output_tokens"),
                )

            return ImageGenerationChunk(content=artifact, usage=usage)

        logger.warning("Unknown event type: %s", event_type)
        return None

    def _parse_usage(self, chunks: list[ImageGenerationChunk]) -> ImageGenerationUsage:
        """Parse usage from chunks.

        Usage is only available in the final completed event.
        """
        # Look for usage in final chunk (completed event)
        for chunk in reversed(chunks):
            if chunk.usage is not None:
                return chunk.usage

        # No usage found
        return ImageGenerationUsage()


__all__ = ["OpenAIImageGenerationStream"]
