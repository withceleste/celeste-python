"""BytePlus Images API parameter mappers."""

from celeste.parameters import FieldMapper
from celeste.types import ImageContent


class SizeMapper(FieldMapper[ImageContent]):
    """Map size to BytePlus size field."""

    field = "size"


class WatermarkMapper(FieldMapper[ImageContent]):
    """Map watermark to BytePlus watermark field."""

    field = "watermark"


class OutputFormatMapper(FieldMapper[ImageContent]):
    """Map output format to BytePlus output_format field."""

    field = "output_format"


class BackgroundMapper(FieldMapper[ImageContent]):
    """Map background handling to BytePlus background field."""

    field = "background"


__all__ = [
    "BackgroundMapper",
    "OutputFormatMapper",
    "SizeMapper",
    "WatermarkMapper",
]
