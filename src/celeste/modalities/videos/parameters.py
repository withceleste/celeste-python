"""Parameters for videos modality."""

from enum import StrEnum

from celeste.artifacts import ImageArtifact
from celeste.parameters import Parameters


class VideoParameter(StrEnum):
    """Unified parameter names for video generation."""

    ASPECT_RATIO = "aspect_ratio"
    RESOLUTION = "resolution"
    DURATION = "duration"
    REFERENCE_IMAGES = "reference_images"
    FIRST_FRAME = "first_frame"
    LAST_FRAME = "last_frame"


class VideoParameters(Parameters):
    """Parameters for video generation operations."""

    aspect_ratio: str
    resolution: str
    duration: int
    reference_images: list[ImageArtifact]
    first_frame: ImageArtifact
    last_frame: ImageArtifact


__all__ = [
    "VideoParameter",
    "VideoParameters",
]
