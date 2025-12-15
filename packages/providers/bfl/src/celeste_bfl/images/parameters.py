"""BFL Images API parameter mappers."""

from typing import Any

from celeste.constraints import Int
from celeste.models import Model
from celeste.parameters import ParameterMapper


class WidthMapper(ParameterMapper):
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


class HeightMapper(ParameterMapper):
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


class PromptUpsamplingMapper(ParameterMapper):
    """Map prompt_upsampling to BFL prompt_upsampling field."""

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
    """Map seed to BFL seed field."""

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
    """Map safety_tolerance to BFL safety_tolerance field."""

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
    """Map output_format to BFL output_format field."""

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
    """Map steps to BFL steps field."""

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
    """Map guidance to BFL guidance field."""

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
