"""Google parameter mappers for image generation."""

from typing import Any

from celeste import Model
from celeste.parameters import ParameterMapper
from celeste_image_generation.parameters import ImageGenerationParameter


class AspectRatioMapper(ParameterMapper):
    """Map aspect_ratio parameter with validation."""

    name = ImageGenerationParameter.ASPECT_RATIO

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

        if "generationConfig" in request:
            request.setdefault("generationConfig", {}).setdefault("imageConfig", {})[
                "aspectRatio"
            ] = validated_value
        else:
            request.setdefault("parameters", {})["aspectRatio"] = validated_value

        return request


class QualityMapper(ParameterMapper):
    """Map quality parameter to imageSize."""

    name = ImageGenerationParameter.QUALITY

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform quality into provider imageSize request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        if "generationConfig" in request:
            request.setdefault("generationConfig", {}).setdefault("imageConfig", {})[
                "imageSize"
            ] = validated_value
        else:
            request.setdefault("parameters", {})["imageSize"] = validated_value

        return request


GOOGLE_PARAMETER_MAPPERS: list[ParameterMapper] = [
    AspectRatioMapper(),
    QualityMapper(),
]

__all__ = ["GOOGLE_PARAMETER_MAPPERS"]
