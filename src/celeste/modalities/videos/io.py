"""IO types for videos modality."""

from pydantic import Field

from celeste.artifacts import Artifact, VideoArtifact
from celeste.io import Chunk, FinishReason, Input, Output, Usage
from celeste.mime_types import ApplicationMimeType


class VideoDraftCache(Artifact):
    """Opaque provider state used to render a prior video draft."""

    mime_type: ApplicationMimeType | None = ApplicationMimeType.OCTET_STREAM


class VideoInput(Input):
    """Input for video generation, editing, and draft enhancement."""

    prompt: str | None = None
    video: VideoArtifact | None = None  # For edit operations
    draft_cache: VideoDraftCache | None = None


class VideoFinishReason(FinishReason):
    """Video generation finish reason."""

    reason: str | None = None
    message: str | None = None


class VideoUsage(Usage):
    """Video generation usage metrics.

    All fields optional since providers vary.
    """

    total_tokens: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    reasoning_tokens: int | None = None
    cached_tokens: int | None = None
    billed_units: float | None = None
    input_mp: float | None = None
    output_mp: float | None = None


class VideoOutput(Output[VideoArtifact]):
    """Output from video generation operations."""

    usage: VideoUsage = Field(default_factory=VideoUsage)
    finish_reason: VideoFinishReason | None = None

    @property
    def draft_cache(self) -> VideoDraftCache | None:
        """Return reusable draft state when the provider supplied it."""
        value = self.metadata.get("draft_cache")
        return value if isinstance(value, VideoDraftCache) else None


class VideoChunk(Chunk[VideoArtifact]):
    """Chunk for video streaming (not typically used - video generation doesn't stream)."""

    finish_reason: VideoFinishReason | None = None
    usage: VideoUsage | None = None


__all__ = [
    "VideoChunk",
    "VideoDraftCache",
    "VideoFinishReason",
    "VideoInput",
    "VideoOutput",
    "VideoUsage",
]
