"""Input and output types for image generation."""

from celeste.artifacts import ImageArtifact
from celeste.io import Chunk, FinishReason, Input, Output, Usage


class ImageGenerationInput(Input):
    """Input for image generation operations."""

    prompt: str


class ImageGenerationFinishReason(FinishReason):
    """Image generation finish reason.

    Stores raw provider reason. Providers map their values in implementation.
    """

    reason: str
    message: str | None = None


class ImageGenerationUsage(Usage):
    """Image generation usage metrics.

    All fields optional since providers vary.
    """

    total_tokens: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    generated_images: int | None = None


class ImageGenerationOutput(Output[ImageArtifact]):
    """Output with ImageArtifact content."""

    pass


class ImageGenerationChunk(Chunk[ImageArtifact]):
    """Typed chunk for image generation streaming."""

    finish_reason: ImageGenerationFinishReason | None = None
    usage: ImageGenerationUsage | None = None


__all__ = [
    "ImageGenerationChunk",
    "ImageGenerationFinishReason",
    "ImageGenerationInput",
    "ImageGenerationOutput",
    "ImageGenerationUsage",
]
