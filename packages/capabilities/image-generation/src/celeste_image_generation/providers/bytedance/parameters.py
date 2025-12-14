"""ByteDance parameter mappers for image generation."""

from typing import Any

from celeste import Model
from celeste.parameters import ParameterMapper
from celeste_image_generation.parameters import ImageGenerationParameter


class AspectRatioMapper(ParameterMapper):
    """Map aspect_ratio to dimension string.

    Accepts freeform dimension strings (e.g., "2048x2048", "3840x2160")
    validated by Dimensions constraint against ByteDance's pixel and aspect ratio bounds.
    """

    name = ImageGenerationParameter.ASPECT_RATIO

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform aspect_ratio into provider request.

        The Dimensions constraint validates:
        - Format: "WIDTHxHEIGHT"
        - Total pixels: [921,600, 16,777,216]
        - Aspect ratio: [1/16, 16]
        """
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        # Transform to provider-specific request format (top-level field)
        request["size"] = validated_value
        return request


class QualityMapper(ParameterMapper):
    """Map quality parameter with validation."""

    name = ImageGenerationParameter.QUALITY

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform quality into provider request.

        Maps quality levels ("1K", "2K", "4K") to ByteDance's size parameter.
        Skips if size is already set by aspect_ratio (conflict resolution).
        """
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        # Skip if size already set by aspect_ratio parameter (conflict resolution)
        if "size" in request:
            return request

        # Transform to provider-specific request format (top-level field)
        request["size"] = validated_value
        return request


class WatermarkMapper(ParameterMapper):
    """Map watermark parameter with validation."""

    name = ImageGenerationParameter.WATERMARK

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform watermark into provider request.

        Adds "AI generated" watermark to bottom-right corner when true.
        Default is true if omitted.
        """
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        # Transform to provider-specific request format (top-level field)
        request["watermark"] = validated_value
        return request


BYTEDANCE_PARAMETER_MAPPERS: list[ParameterMapper] = [
    AspectRatioMapper(),
    QualityMapper(),
    WatermarkMapper(),
]

__all__ = ["BYTEDANCE_PARAMETER_MAPPERS"]
