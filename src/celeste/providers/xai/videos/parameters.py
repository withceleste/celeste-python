"""xAI Videos API parameter mappers."""

from celeste.parameters import FieldMapper


class DurationMapper(FieldMapper):
    """Map duration to xAI duration field."""

    field = "duration"


class AspectRatioMapper(FieldMapper):
    """Map aspect_ratio to xAI aspect_ratio field."""

    field = "aspect_ratio"


class ResolutionMapper(FieldMapper):
    """Map resolution to xAI resolution field."""

    field = "resolution"


__all__ = [
    "AspectRatioMapper",
    "DurationMapper",
    "ResolutionMapper",
]
