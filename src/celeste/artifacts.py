"""Unified artifact types for Celeste."""

import base64
from typing import Any

from pydantic import BaseModel, Field, field_serializer

from celeste.mime_types import (
    AudioMimeType,
    ImageMimeType,
    MimeType,
    VideoMimeType,
)


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

    @field_serializer("data", when_used="json")
    def serialize_data(self, value: bytes | None) -> str | None:
        """Serialize bytes as base64 string for JSON compatibility."""
        if value is None:
            return None
        return base64.b64encode(value).decode("ascii")

    @property
    def has_content(self) -> bool:
        """Check if artifact has any content."""
        return bool(
            (self.url and self.url.strip())
            or self.data
            or (self.path and self.path.strip())
        )

    def get_bytes(self) -> bytes:
        """Get raw bytes, reading from path if needed.

        Raises:
            ValueError: If artifact has no data or path.
        """
        if self.data:
            return self.data
        if self.path:
            with open(self.path, "rb") as f:
                return f.read()
        msg = "Artifact must have data or path to get bytes"
        raise ValueError(msg)

    def get_base64(self) -> str:
        """Get base64-encoded string of the content."""
        return base64.b64encode(self.get_bytes()).decode("utf-8")


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
