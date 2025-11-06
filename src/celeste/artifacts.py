"""Unified artifact types for Celeste."""

from typing import Any

from pydantic import BaseModel, Field

from celeste.mime_types import AudioMimeType, ImageMimeType, MimeType, VideoMimeType


class Artifact(BaseModel):
    """Base class for all media artifacts.

    Artifacts can be represented in three ways:
    - url: Remote HTTP/HTTPS URL (may expire, e.g., DALL-E URLs last 1 hour)
    - data: In-memory bytes (for immediate use without download)
    - path: Local filesystem path (for local providers or saved files)

    Providers typically populate only one of these fields.
    """

    url: str | None = None
    data: bytes | None = None
    path: str | None = None
    mime_type: MimeType | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def has_content(self) -> bool:
        """Check if artifact has any content."""
        return bool(
            (self.url and self.url.strip())
            or self.data
            or (self.path and self.path.strip())
        )


class ImageArtifact(Artifact):
    """Image artifact from generation/edit operations."""

    mime_type: ImageMimeType | None = None


class VideoArtifact(Artifact):
    """Video artifact from generation operations."""

    mime_type: VideoMimeType | None = None


class AudioArtifact(Artifact):
    """Audio artifact from TTS/transcription operations."""

    mime_type: AudioMimeType | None = None


__all__ = [
    "Artifact",
    "AudioArtifact",
    "ImageArtifact",
    "VideoArtifact",
]
