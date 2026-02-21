"""BytePlus Images API parameter mappers."""

from celeste.parameters import FieldMapper


class SizeMapper(FieldMapper):
    """Map size to BytePlus size field."""

    field = "size"


class WatermarkMapper(FieldMapper):
    """Map watermark to BytePlus watermark field."""

    field = "watermark"


__all__ = ["SizeMapper", "WatermarkMapper"]
