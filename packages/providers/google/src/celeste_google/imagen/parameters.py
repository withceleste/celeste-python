"""Google Imagen API parameter mappers."""

from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper


class SampleCountMapper(ParameterMapper):
    """Map num_images to Google Imagen parameters.sampleCount field."""

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

        request.setdefault("parameters", {})["sampleCount"] = validated_value
        return request


class AspectRatioMapper(ParameterMapper):
    """Map aspect_ratio to Google Imagen parameters.aspectRatio field."""

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

        request.setdefault("parameters", {})["aspectRatio"] = validated_value
        return request


class ImageSizeMapper(ParameterMapper):
    """Map image_size to Google Imagen parameters.imageSize field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform image_size into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request.setdefault("parameters", {})["imageSize"] = validated_value
        return request


__all__ = [
    "AspectRatioMapper",
    "ImageSizeMapper",
    "SampleCountMapper",
]
