"""Ollama Generate API parameter mappers.

Naming convention:
- Mapper class name MUST match the provider's API parameter name
- Example: API param "width" → class WidthMapper
- The request key should match the provider's expected field name exactly
"""

from typing import Any

from celeste.constraints import Int
from celeste.models import Model
from celeste.parameters import ParameterMapper


class WidthMapper(ParameterMapper):
    """Map width to Ollama width field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform width into provider request."""
        if value is None:
            return request

        request["width"] = Int()(value)
        return request


class HeightMapper(ParameterMapper):
    """Map height to Ollama height field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform height into provider request."""
        if value is None:
            return request

        request["height"] = Int()(value)
        return request


class StepsMapper(ParameterMapper):
    """Map steps to Ollama steps field."""

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


class SeedMapper(ParameterMapper):
    """Map seed to Ollama options.seed field (nested)."""

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

        request.setdefault("options", {})["seed"] = validated_value
        return request


class NegativePromptMapper(ParameterMapper):
    """Map negative_prompt to Ollama negative_prompt field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform negative_prompt into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["negative_prompt"] = validated_value
        return request


__all__ = [
    "HeightMapper",
    "NegativePromptMapper",
    "SeedMapper",
    "StepsMapper",
    "WidthMapper",
]
