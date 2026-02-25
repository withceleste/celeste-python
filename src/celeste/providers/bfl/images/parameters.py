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


class PromptUpsamplingMapper(FieldMapper[ImageContent]):
    """Map prompt_upsampling to BFL prompt_upsampling field."""

    field = "prompt_upsampling"


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
    "GuidanceMapper",
    "HeightMapper",
    "OutputFormatMapper",
    "PromptUpsamplingMapper",
    "SafetyToleranceMapper",
    "SeedMapper",
    "StepsMapper",
    "WidthMapper",
]
