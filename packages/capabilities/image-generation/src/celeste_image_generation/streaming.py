"""Streaming for image generation."""

from abc import abstractmethod
from typing import Unpack

from celeste.streaming import Stream
from celeste_image_generation.io import (
    ImageGenerationChunk,
    ImageGenerationOutput,
    ImageGenerationUsage,
)
from celeste_image_generation.parameters import ImageGenerationParameters


class ImageGenerationStream(
    Stream[ImageGenerationOutput, ImageGenerationParameters, ImageGenerationChunk]
):
    """Streaming for image generation."""

    def _parse_output(  # type: ignore[override]
        self,
        chunks: list[ImageGenerationChunk],
        **parameters: Unpack[ImageGenerationParameters],
    ) -> ImageGenerationOutput:
        """Assemble chunks into final output.

        For image generation, the final chunk contains the complete image.
        Progressive chunks may contain partial/preview images.
        """
        if not chunks:
            msg = "No chunks received from stream"
            raise ValueError(msg)

        # Final chunk contains complete image
        content = chunks[-1].content
        usage = self._parse_usage(chunks)
        finish_reason = chunks[-1].finish_reason if chunks else None

        return ImageGenerationOutput(
            content=content,
            usage=usage,
            finish_reason=finish_reason,
            metadata={},
        )

    @abstractmethod
    def _parse_usage(self, chunks: list[ImageGenerationChunk]) -> ImageGenerationUsage:
        """Parse usage from chunks (provider-specific)."""


__all__ = ["ImageGenerationStream"]
