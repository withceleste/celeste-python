"""OpenAI Images API parameter mappers."""

from celeste.parameters import FieldMapper


class SizeMapper(FieldMapper):
    """Map size to OpenAI size field."""

    field = "size"


class PartialImagesMapper(FieldMapper):
    """Map partial_images to OpenAI partial_images field."""

    field = "partial_images"


class QualityMapper(FieldMapper):
    """Map quality to OpenAI quality field."""

    field = "quality"


class BackgroundMapper(FieldMapper):
    """Map background to OpenAI background field."""

    field = "background"


class OutputFormatMapper(FieldMapper):
    """Map output_format to OpenAI output_format field."""

    field = "output_format"


class StyleMapper(FieldMapper):
    """Map style to OpenAI style field."""

    field = "style"


class ModerationMapper(FieldMapper):
    """Map moderation to OpenAI moderation field."""

    field = "moderation"


class OutputCompressionMapper(FieldMapper):
    """Map output_compression to OpenAI output_compression field."""

    field = "output_compression"


__all__ = [
    "BackgroundMapper",
    "ModerationMapper",
    "OutputCompressionMapper",
    "OutputFormatMapper",
    "PartialImagesMapper",
    "QualityMapper",
    "SizeMapper",
    "StyleMapper",
]
