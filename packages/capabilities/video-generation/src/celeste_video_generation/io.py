"""Input and output types for video generation."""

from pydantic import Field

from celeste.artifacts import VideoArtifact
from celeste.io import Input, Output, Usage


class VideoGenerationInput(Input):
    """Input for video generation operations."""

    prompt: str


class VideoGenerationUsage(Usage):
    """Video generation usage metrics.

    All fields optional since providers vary.
    """

    total_tokens: int | None = None
    billing_units: float | None = None


class VideoGenerationOutput(Output[VideoArtifact]):
    """Output with VideoArtifact content."""

    usage: VideoGenerationUsage = Field(default_factory=VideoGenerationUsage)


__all__ = [
    "VideoGenerationInput",
    "VideoGenerationOutput",
    "VideoGenerationUsage",
]
