"""MIME type enumerations for Celeste."""

from enum import StrEnum


class MimeType(StrEnum):
    """Base class for all MIME types."""


class ApplicationMimeType(MimeType):
    """Standard MIME types for application data."""

    JSON = "application/json"


class ImageMimeType(MimeType):
    """Standard MIME types for images."""

    PNG = "image/png"
    JPEG = "image/jpeg"
    WEBP = "image/webp"
    BMP = "image/bmp"
    TIFF = "image/tiff"
    GIF = "image/gif"


class VideoMimeType(MimeType):
    """Standard MIME types for videos."""

    MP4 = "video/mp4"
    AVI = "video/x-msvideo"
    MOV = "video/quicktime"


class AudioMimeType(MimeType):
    """Standard MIME types for audio."""

    MP3 = "audio/mpeg"
    WAV = "audio/wav"
    OGG = "audio/ogg"
    WEBM = "audio/webm"
    AAC = "audio/aac"
    FLAC = "audio/flac"
    AIFF = "audio/aiff"
    M4A = "audio/mp4"
    WMA = "audio/x-ms-wma"
    PCM = "audio/pcm"


__all__ = [
    "ApplicationMimeType",
    "AudioMimeType",
    "ImageMimeType",
    "MimeType",
    "VideoMimeType",
]
