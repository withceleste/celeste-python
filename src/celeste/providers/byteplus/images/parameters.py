"""BytePlus Images API parameter mappers."""

from celeste.parameters import FieldMapper
from celeste.types import ImageContent


class SizeMapper(FieldMapper[ImageContent]):
    """Map size to BytePlus size field."""

    field = "size"


class WatermarkMapper(FieldMapper[ImageContent]):
    """Map watermark to BytePlus watermark field."""

    field = "watermark"


__all__ = ["SizeMapper", "WatermarkMapper"]
