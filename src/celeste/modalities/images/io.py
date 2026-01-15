"""IO types for images modality."""

from pydantic import Field

from celeste.artifacts import ImageArtifact
from celeste.io import Chunk, FinishReason, Input, Output, Usage
from celeste.types import ImageContent


class ImageInput(Input):
    """Input for images operations."""

    prompt: str
    image: ImageArtifact | None = None


class ImageFinishReason(FinishReason):
    """Images finish reason."""

    reason: str | None = None
    message: str | None = None


class ImageUsage(Usage):
    """Images usage metrics."""

    total_tokens: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    reasoning_tokens: int | None = None
    num_images: int | None = None
    billed_units: float | None = None
    input_mp: float | None = None
    output_mp: float | None = None


class ImageOutput(Output[ImageContent]):
    """Output from images operations."""

    usage: ImageUsage = Field(default_factory=ImageUsage)
    finish_reason: ImageFinishReason | None = None


class ImageChunk(Chunk[ImageArtifact]):
    """Chunk for images streaming."""

    finish_reason: ImageFinishReason | None = None
    usage: ImageUsage | None = None


__all__ = [
    "ImageChunk",
    "ImageFinishReason",
    "ImageInput",
    "ImageOutput",
    "ImageUsage",
]
