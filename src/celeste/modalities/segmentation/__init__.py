"""Celeste Segmentation modality."""

from .client import SegmentationClient
from .io import (
    SegmentationChunk,
    SegmentationFinishReason,
    SegmentationInput,
    SegmentationOutput,
    SegmentationUsage,
)
from .parameters import (
    BoxPrompt,
    PointPrompt,
    SegmentationParameter,
    SegmentationParameters,
)

__all__ = [
    "BoxPrompt",
    "PointPrompt",
    "SegmentationChunk",
    "SegmentationClient",
    "SegmentationFinishReason",
    "SegmentationInput",
    "SegmentationOutput",
    "SegmentationParameter",
    "SegmentationParameters",
    "SegmentationUsage",
]
