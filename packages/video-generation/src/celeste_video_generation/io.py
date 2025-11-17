"""Input and output types for video generation."""

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

    pass


__all__ = [
    "VideoGenerationInput",
    "VideoGenerationOutput",
    "VideoGenerationUsage",
]
