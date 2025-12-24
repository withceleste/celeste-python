"""Input and output types for image generation."""

from pydantic import Field

from celeste.artifacts import ImageArtifact
from celeste.io import Chunk, FinishReason, Input, Output, Usage


class ImageGenerationInput(Input):
    """Input for image generation operations."""

    prompt: str


class ImageGenerationFinishReason(FinishReason):
    """Image generation finish reason.

    Stores raw provider reason. Providers map their values in implementation.
    """

    reason: str | None = None
    message: str | None = None


class ImageGenerationUsage(Usage):
    """Image generation usage metrics.

    All fields optional since providers vary.
    """

    total_tokens: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    reasoning_tokens: int | None = None
    num_images: int | None = None
    billed_units: float | None = None
    input_mp: float | None = None
    output_mp: float | None = None


class ImageGenerationOutput(Output[ImageArtifact | list[ImageArtifact]]):
    """Output with ImageArtifact content (single or multiple)."""

    usage: ImageGenerationUsage = Field(default_factory=ImageGenerationUsage)
    finish_reason: ImageGenerationFinishReason | None = None


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
