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
    """Map ratios or exact pixel dimensions to the model's BFL fields."""

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

        if model.id in {"flux-kontext-pro", "flux-kontext-max", "flux-pro-1.1-ultra"}:
            request["aspect_ratio"] = validated_value
            return request

        width, height = validated_value.split("x")
        request = WidthMapper().map(request, width, model)
        return HeightMapper().map(request, height, model)


class PromptUpsamplingMapper(FieldMapper[ImageContent]):
    """Map prompt rewriting to the model's native control and polarity."""

    field = "prompt_upsampling"

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform prompt_upsampling into provider request."""
        if model.id in {"flux-2-max", "flux-2-pro", "flux-2-pro-preview"}:
            validated_value = self._validate_value(value, model)
            if validated_value is not None:
                request["disable_pup"] = not validated_value
            return request
        if model.id in {
            "flux-2-klein-4b",
            "flux-2-klein-9b",
            "flux-2-klein-9b-preview",
        }:
            return request
        return super().map(request, value, model)


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
