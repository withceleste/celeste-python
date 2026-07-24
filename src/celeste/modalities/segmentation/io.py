"""IO types for segmentation modality."""

from pydantic import Field

from celeste.artifacts import ImageArtifact
from celeste.io import Chunk, FinishReason, Input, Output, Usage
from celeste.types import SegmentationContent


class SegmentationInput(Input):
    """Input for segmentation operations."""

    image: ImageArtifact
    prompt: str | None = None


class SegmentationFinishReason(FinishReason):
    """Segmentation finish reason."""

    reason: str | None = None
    message: str | None = None


class SegmentationUsage(Usage):
    """Segmentation usage metrics."""

    billed_units: float | None = None


class SegmentationOutput(Output[SegmentationContent]):
    """Output from segmentation operations."""

    usage: SegmentationUsage = Field(default_factory=SegmentationUsage)
    finish_reason: SegmentationFinishReason | None = None


class SegmentationChunk(Chunk[SegmentationContent]):
    """Chunk for segmentation streaming (unused in v1)."""

    finish_reason: SegmentationFinishReason | None = None
    usage: SegmentationUsage | None = None


__all__ = [
    "SegmentationChunk",
    "SegmentationFinishReason",
    "SegmentationInput",
    "SegmentationOutput",
    "SegmentationUsage",
]
