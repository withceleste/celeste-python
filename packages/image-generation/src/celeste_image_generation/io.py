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

    reason: str | None = (
        None  # Raw provider string (e.g., "STOP", "NO_IMAGE", "PROHIBITED_CONTENT")
    )
    message: str | None = None  # Optional human-readable explanation from provider


class ImageGenerationUsage(Usage):
    """Image generation usage metrics.

    Most providers don't report usage metrics for image generation.
    OpenAI gpt-image-1 reports usage only in streaming mode.
    ByteDance reports tokens_used for billing tracking.
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
