"""xAI Images API parameter mappers.

Naming convention:
- Mapper class name MUST match the provider's API parameter name
- Example: API param "aspect_ratio" → class AspectRatioMapper
- The request key should match the provider's expected field name exactly
"""

from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper


class AspectRatioMapper(ParameterMapper):
    """Map aspect_ratio to xAI aspect_ratio field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform aspect_ratio into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["aspect_ratio"] = validated_value
        return request


class NumImagesMapper(ParameterMapper):
    """Map num_images to xAI n field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform num_images into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["n"] = validated_value
        return request


class ResponseFormatMapper(ParameterMapper):
    """Map response_format to xAI response_format field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform response_format into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["response_format"] = validated_value
        return request


__all__ = [
    "AspectRatioMapper",
    "NumImagesMapper",
    "ResponseFormatMapper",
]
