"""Ollama Generate API parameter mappers.

Naming convention:
- Mapper class name MUST match the provider's API parameter name
- Example: API param "width" → class WidthMapper
- The request key should match the provider's expected field name exactly
"""

from typing import Any

from celeste.constraints import Int
from celeste.models import Model
from celeste.parameters import FieldMapper, ParameterMapper
from celeste.types import ImageContent


class WidthMapper(ParameterMapper[ImageContent]):
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


class HeightMapper(ParameterMapper[ImageContent]):
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


class StepsMapper(FieldMapper[ImageContent]):
    """Map steps to Ollama steps field."""

    field = "steps"


class SeedMapper(ParameterMapper[ImageContent]):
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


class NegativePromptMapper(FieldMapper[ImageContent]):
    """Map negative_prompt to Ollama negative_prompt field."""

    field = "negative_prompt"


__all__ = [
    "HeightMapper",
    "NegativePromptMapper",
    "SeedMapper",
    "StepsMapper",
    "WidthMapper",
]
