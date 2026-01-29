"""IO types for videos modality."""

from pydantic import Field

from celeste.artifacts import VideoArtifact
from celeste.io import Chunk, FinishReason, Input, Output, Usage


class VideoInput(Input):
    """Input for video generation and edit operations."""

    prompt: str
    video: VideoArtifact | None = None  # For edit operations


class VideoFinishReason(FinishReason):
    """Video generation finish reason."""

    reason: str | None = None
    message: str | None = None


class VideoUsage(Usage):
    """Video generation usage metrics.

    All fields optional since providers vary.
    """

    total_tokens: int | None = None
    billed_units: float | None = None


class VideoOutput(Output[VideoArtifact]):
    """Output from video generation operations."""

    usage: VideoUsage = Field(default_factory=VideoUsage)
    finish_reason: VideoFinishReason | None = None


class VideoChunk(Chunk[VideoArtifact]):
    """Chunk for video streaming (not typically used - video generation doesn't stream)."""

    finish_reason: VideoFinishReason | None = None
    usage: VideoUsage | None = None


__all__ = [
    "VideoChunk",
    "VideoFinishReason",
    "VideoInput",
    "VideoOutput",
    "VideoUsage",
]
