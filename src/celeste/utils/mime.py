"""MIME type detection utilities."""

import filetype

from celeste.artifacts import ImageArtifact
from celeste.mime_types import AudioMimeType, ImageMimeType, MimeType, VideoMimeType


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
    for mime_enum in (ImageMimeType, VideoMimeType, AudioMimeType):
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

    for mime_enum in (ImageMimeType, VideoMimeType, AudioMimeType):
        try:
            return mime_enum(mime_str)
        except ValueError:
            continue

    return None


def build_image_data_url(img: ImageArtifact) -> str:
    """Build a data URL from an ImageArtifact.

    For images with only a URL (no data or path), returns the URL directly.
    For images with data or path, builds a data URL with MIME type detection.
    """

    if img.url and not img.data and not img.path:
        return img.url

    image_bytes = img.get_bytes()
    mime = img.mime_type or detect_mime_type(image_bytes)
    mime_str = mime.value if mime else ""

    return f"data:{mime_str};base64,{img.get_base64()}"


__all__ = ["build_image_data_url", "detect_mime_type", "detect_mime_type_from_path"]
