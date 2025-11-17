"""Parameters for video generation."""

from enum import StrEnum

from celeste.artifacts import ImageArtifact
from celeste.parameters import Parameters


class VideoGenerationParameter(StrEnum):
    """Unified parameter names for video generation capability."""

    ASPECT_RATIO = "aspect_ratio"
    RESOLUTION = "resolution"
    DURATION = "duration"
    REFERENCE_IMAGES = "reference_images"
    FIRST_FRAME = "first_frame"
    LAST_FRAME = "last_frame"


class VideoGenerationParameters(Parameters):
    """Parameters for video generation."""

    aspect_ratio: str | None
    resolution: str | None
    duration: int | None
    reference_images: list[ImageArtifact] | None
    first_frame: ImageArtifact | None
    last_frame: ImageArtifact | None
