"""BFL Images API parameter mappers."""

from typing import Any

from celeste.constraints import Int
from celeste.models import Model
from celeste.parameters import FieldMapper, ParameterMapper
from celeste.types import ImageContent


class WidthMapper(ParameterMapper[ImageContent]):
    """Map width to BFL width field."""

    def map(
        self,
        request: dict[str, Any],
        value: int | str | float | None,
        model: Model,
    ) -> dict[str, Any]:
        """Transform width into provider request."""
        if value is None:
            return request

        request["width"] = Int()(value)
        return request


class HeightMapper(ParameterMapper[ImageContent]):
    """Map height to BFL height field."""

    def map(
        self,
        request: dict[str, Any],
        value: int | str | float | None,
        model: Model,
    ) -> dict[str, Any]:
        """Transform height into provider request."""
        if value is None:
            return request

        request["height"] = Int()(value)
        return request


class AspectRatioMapper(ParameterMapper[ImageContent]):
    """Map native ratios or validated pixel dimensions for the BFL family."""

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request
        if model.id in ("flux-kontext-pro", "flux-kontext-max", "flux-pro-1.1-ultra"):
            request["aspect_ratio"] = validated_value
        else:
            width, height = validated_value.split("x")
            request = WidthMapper().map(request, width, model)
            request = HeightMapper().map(request, height, model)
        return request


class PromptUpsamplingMapper(ParameterMapper[ImageContent]):
    """Map the prompt control supported by each BFL family."""

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        validated_value = self._validate_value(value, model)
        if validated_value is None or model.id.startswith("flux-2-klein-"):
            return request
        if model.id in ("flux-2-max", "flux-2-pro", "flux-2-pro-preview"):
            request["disable_pup"] = not validated_value
        else:
            request["prompt_upsampling"] = validated_value
        return request


class SeedMapper(FieldMapper[ImageContent]):
    """Map seed to BFL seed field."""

    field = "seed"


class SafetyToleranceMapper(FieldMapper[ImageContent]):
    """Map safety_tolerance to BFL safety_tolerance field."""

    field = "safety_tolerance"


class OutputFormatMapper(FieldMapper[ImageContent]):
    """Map output_format to BFL output_format field."""

    field = "output_format"


class StepsMapper(FieldMapper[ImageContent]):
    """Map steps to BFL steps field."""

    field = "steps"


class GuidanceMapper(FieldMapper[ImageContent]):
    """Map guidance to BFL guidance field."""

    field = "guidance"


__all__ = [
    "AspectRatioMapper",
    "GuidanceMapper",
    "HeightMapper",
    "OutputFormatMapper",
    "PromptUpsamplingMapper",
    "SafetyToleranceMapper",
    "SeedMapper",
    "StepsMapper",
    "WidthMapper",
]
