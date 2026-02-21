"""xAI Images API parameter mappers.

Naming convention:
- Mapper class name MUST match the provider's API parameter name
- Example: API param "aspect_ratio" → class AspectRatioMapper
- The request key should match the provider's expected field name exactly
"""

from celeste.parameters import FieldMapper


class AspectRatioMapper(FieldMapper):
    """Map aspect_ratio to xAI aspect_ratio field."""

    field = "aspect_ratio"


class NumImagesMapper(FieldMapper):
    """Map num_images to xAI n field."""

    field = "n"


class ResponseFormatMapper(FieldMapper):
    """Map response_format to xAI response_format field."""

    field = "response_format"


__all__ = [
    "AspectRatioMapper",
    "NumImagesMapper",
    "ResponseFormatMapper",
]
