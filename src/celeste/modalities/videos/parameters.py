"""Parameters for videos modality."""

from enum import StrEnum
from typing import Annotated

from pydantic import Field

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


class VideoParameters(Parameters, total=False):
    """Parameters for video generation operations."""

    aspect_ratio: Annotated[
        str, Field(description="Output video dimensions or aspect ratio.")
    ]
    resolution: Annotated[str, Field(description="Vertical resolution tier.")]
    duration: Annotated[int, Field(description="Clip length in seconds.")]
    reference_images: Annotated[
        list[ImageArtifact],
        Field(description="Additional images conditioning the video."),
    ]
    first_frame: Annotated[
        ImageArtifact, Field(description="Image to use as the video's first frame.")
    ]
    last_frame: Annotated[
        ImageArtifact, Field(description="Image to use as the video's last frame.")
    ]


__all__ = [
    "VideoParameter",
    "VideoParameters",
]
