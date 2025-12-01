"""BFL parameter mappers for image generation."""

from typing import Any

from celeste import Model
from celeste.parameters import ParameterMapper
from celeste_image_generation.parameters import ImageGenerationParameter


class AspectRatioMapper(ParameterMapper):
    """Map aspect_ratio to BFL width/height parameters."""

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

        parts = validated_value.split("x")
        width = int(parts[0])
        height = int(parts[1])

        # Round to nearest multiple of 16 as required by BFL API
        width = ((width + 8) // 16) * 16
        height = ((height + 8) // 16) * 16

        request["width"] = width
        request["height"] = height
        return request


class PromptUpsamplingMapper(ParameterMapper):
    """Map prompt_upsampling parameter to BFL request format."""

    name = ImageGenerationParameter.PROMPT_UPSAMPLING

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform prompt_upsampling into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["prompt_upsampling"] = validated_value
        return request


class SeedMapper(ParameterMapper):
    """Map seed parameter to BFL request format."""

    name = ImageGenerationParameter.SEED

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform seed into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["seed"] = validated_value
        return request


class SafetyToleranceMapper(ParameterMapper):
    """Map safety_tolerance parameter to BFL request format."""

    name = ImageGenerationParameter.SAFETY_TOLERANCE

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform safety_tolerance into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["safety_tolerance"] = validated_value
        return request


class OutputFormatMapper(ParameterMapper):
    """Map output_format parameter to BFL request format."""

    name = ImageGenerationParameter.OUTPUT_FORMAT

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform output_format into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["output_format"] = validated_value
        return request


class StepsMapper(ParameterMapper):
    """Map steps parameter to BFL request format (flex only)."""

    name = ImageGenerationParameter.STEPS

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform steps into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["steps"] = validated_value
        return request


class GuidanceMapper(ParameterMapper):
    """Map guidance parameter to BFL request format (flex only)."""

    name = ImageGenerationParameter.GUIDANCE

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform guidance into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["guidance"] = validated_value
        return request


BFL_PARAMETER_MAPPERS: list[ParameterMapper] = [
    AspectRatioMapper(),
    PromptUpsamplingMapper(),
    SeedMapper(),
    SafetyToleranceMapper(),
    OutputFormatMapper(),
    StepsMapper(),
    GuidanceMapper(),
]

__all__ = ["BFL_PARAMETER_MAPPERS"]
