"""xAI Images API parameter mappers.

Naming convention:
- Mapper class name MUST match the provider's API parameter name
- Example: API param "aspect_ratio" → class AspectRatioMapper
- The request key should match the provider's expected field name exactly
"""

from typing import Any

from celeste.models import Model
from celeste.parameters import FieldMapper, ParameterMapper
from celeste.types import ImageContent
from celeste.utils import build_data_url


class AspectRatioMapper(FieldMapper[ImageContent]):
    """Map aspect_ratio to xAI aspect_ratio field."""

    field = "aspect_ratio"


class ImagesMapper(ParameterMapper[ImageContent]):
    """Map images to xAI images field, after the edit image if present."""

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Transform images into provider request."""
        validated_value = self._validate_value(value, model)
        if not validated_value:
            return request

        images = [request.pop("image")] if "image" in request else []
        images.extend({"url": build_data_url(image)} for image in validated_value)
        request["images"] = images
        return request


class NumImagesMapper(FieldMapper[ImageContent]):
    """Map num_images to xAI n field."""

    field = "n"


class ResolutionMapper(FieldMapper[ImageContent]):
    """Map resolution to xAI resolution field."""

    field = "resolution"


class ResponseFormatMapper(FieldMapper[ImageContent]):
    """Map response_format to xAI response_format field."""

    field = "response_format"


__all__ = [
    "AspectRatioMapper",
    "ImagesMapper",
    "NumImagesMapper",
    "ResolutionMapper",
    "ResponseFormatMapper",
]
