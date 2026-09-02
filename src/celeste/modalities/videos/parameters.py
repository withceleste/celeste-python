"""Parameters for videos modality."""

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, Field

from celeste.artifacts import ImageArtifact, VideoArtifact
from celeste.parameters import Parameters


class VideoKeyframe(BaseModel):
    """An image pinned to an optional timestamp on a video timeline."""

    image: ImageArtifact
    timestamp: float | None = None


class VideoParameter(StrEnum):
    """Unified parameter names for video generation."""

    ASPECT_RATIO = "aspect_ratio"
    RESOLUTION = "resolution"
    DURATION = "duration"
    REFERENCE_IMAGES = "reference_images"
    FIRST_FRAME = "first_frame"
    LAST_FRAME = "last_frame"
    KEYFRAMES = "keyframes"
    START_VIDEO = "start_video"
    GENERATE_AUDIO = "generate_audio"
    SAFETY_TOLERANCE = "safety_tolerance"
    DRAFT = "draft"


class VideoParameters(Parameters, total=False):
    """Parameters for video generation operations."""

    aspect_ratio: Annotated[
        str, Field(description="Output video dimensions or aspect ratio.")
    ]
    resolution: Annotated[str, Field(description="Vertical resolution tier.")]
    duration: Annotated[
        int | str,
        Field(description="Clip length in seconds, or a provider-supported mode."),
    ]
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
    keyframes: Annotated[
        list[VideoKeyframe],
        Field(description="Ordered images optionally pinned to timeline timestamps."),
    ]
    start_video: Annotated[
        VideoArtifact,
        Field(description="Existing video whose final frames start the generation."),
    ]
    generate_audio: Annotated[
        bool, Field(description="Generate synchronized audio with the video.")
    ]
    safety_tolerance: Annotated[
        int, Field(description="Provider safety tolerance level.")
    ]
    draft: Annotated[
        bool, Field(description="Generate a fast preview with reusable draft state.")
    ]


__all__ = [
    "VideoKeyframe",
    "VideoParameter",
    "VideoParameters",
]
