"""OpenAI parameter mappers for image generation."""

from typing import Any

from celeste import Model
from celeste.parameters import ParameterMapper
from celeste_image_generation.parameters import ImageGenerationParameter


class AspectRatioMapper(ParameterMapper):
    """Map aspect_ratio parameter to OpenAI's size parameter."""

    name = ImageGenerationParameter.ASPECT_RATIO

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform aspect_ratio into provider request.

        Maps unified aspect_ratio parameter to OpenAI's size format.
        Values are OpenAI's native size strings (e.g., "1024x1024", "1792x1024").
        Coercion from ratio format ("16:9") to size format can be added later.

        Args:
            request: Provider request dictionary to modify.
            value: The aspect_ratio value (OpenAI size string).
            model: Model instance with parameter constraints.

        Returns:
            Modified request dictionary with size parameter.
        """
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        # Transform to provider-specific request format (size parameter)
        request["size"] = validated_value
        return request


class PartialImagesMapper(ParameterMapper):
    """Map partial_images parameter for streaming (gpt-image-1 only)."""

    name = ImageGenerationParameter.PARTIAL_IMAGES

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform partial_images into provider request.

        Controls number of partial images during streaming (0-3).
        Only supported by gpt-image-1 model.

        Args:
            request: Provider request dictionary to modify.
            value: The partial_images value (0-3).
            model: Model instance with parameter constraints.

        Returns:
            Modified request dictionary with partial_images parameter.
        """
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        # Transform to provider-specific request format (top-level field)
        request["partial_images"] = validated_value
        return request


class QualityMapper(ParameterMapper):
    """Map quality parameter for DALL-E 3 and gpt-image-1."""

    name = ImageGenerationParameter.QUALITY

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform quality into provider request.

        Controls image quality/detail level.
        - DALL-E 3: "standard" or "hd"
        - gpt-image-1: "low", "medium", "high", or "auto"
        - DALL-E 2: Not supported (no constraint in model)

        Args:
            request: Provider request dictionary to modify.
            value: The quality value.
            model: Model instance with parameter constraints.

        Returns:
            Modified request dictionary with quality parameter.
        """
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        # Transform to provider-specific request format (top-level field)
        request["quality"] = validated_value
        return request


OPENAI_PARAMETER_MAPPERS: list[ParameterMapper] = [
    AspectRatioMapper(),
    PartialImagesMapper(),
    QualityMapper(),
]

__all__ = ["OPENAI_PARAMETER_MAPPERS"]
