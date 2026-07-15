"""MIME type detection utilities."""

import base64

import filetype

from celeste.artifacts import Artifact
from celeste.mime_types import (
    AudioMimeType,
    DocumentMimeType,
    ImageMimeType,
    MimeType,
    VideoMimeType,
)


def detect_mime_type(data: bytes) -> MimeType | None:
    """Detect MIME type from magic bytes.

    Uses the filetype library to detect file type from the first 261 bytes
    of binary data (magic number signatures).

    Args:
        data: Binary data to analyze.

    Returns:
        Detected MimeType or None if unknown.

    Example:
        >>> with open("image.png", "rb") as f:
        ...     mime = detect_mime_type(f.read())
        >>> print(mime)  # ImageMimeType.PNG
    """
    result = filetype.guess(data)
    if result is None:
        return None

    mime_str = result.mime

    # Try to match against our known MIME type enums
    for mime_enum in (ImageMimeType, VideoMimeType, AudioMimeType, DocumentMimeType):
        try:
            return mime_enum(mime_str)
        except ValueError:
            continue

    return None


def detect_mime_type_from_path(path: str) -> MimeType | None:
    """Detect MIME type from a file path.

    Reads the file header and detects type from magic bytes.

    Args:
        path: Path to the file.

    Returns:
        Detected MimeType or None if unknown.
    """
    result = filetype.guess(path)
    if result is None:
        return None

    mime_str = result.mime

    for mime_enum in (ImageMimeType, VideoMimeType, AudioMimeType, DocumentMimeType):
        try:
            return mime_enum(mime_str)
        except ValueError:
            continue

    return None


def build_data_url(artifact: Artifact) -> str:
    """Return a remote URL or encode local artifact content as a data URL."""
    if artifact.url and not artifact.data and not artifact.path:
        return artifact.url

    data = artifact.get_bytes()
    mime = artifact.mime_type or detect_mime_type(data)
    if mime is None:
        msg = "Artifact MIME type must be specified or detectable"
        raise ValueError(msg)
    encoded = base64.b64encode(data).decode("utf-8")
    return f"data:{mime.value};base64,{encoded}"


__all__ = [
    "build_data_url",
    "detect_mime_type",
    "detect_mime_type_from_path",
]
