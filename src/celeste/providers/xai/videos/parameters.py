"""xAI Videos API parameter mappers."""

from celeste.parameters import FieldMapper
from celeste.types import VideoContent


class DurationMapper(FieldMapper[VideoContent]):
    """Map duration to xAI duration field."""

    field = "duration"


class AspectRatioMapper(FieldMapper[VideoContent]):
    """Map aspect_ratio to xAI aspect_ratio field."""

    field = "aspect_ratio"


class ResolutionMapper(FieldMapper[VideoContent]):
    """Map resolution to xAI resolution field."""

    field = "resolution"


__all__ = [
    "AspectRatioMapper",
    "DurationMapper",
    "ResolutionMapper",
]
