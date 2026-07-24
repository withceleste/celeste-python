"""Groq Audio API parameter mappers."""

from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper


class LanguageMapper[Content](ParameterMapper[Content]):
    """Map language to Groq language field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform language into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request
        request["language"] = validated_value
        return request


class PromptMapper[Content](ParameterMapper[Content]):
    """Map prompt to Groq prompt field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform prompt into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request
        request["prompt"] = validated_value
        return request


class TemperatureMapper[Content](ParameterMapper[Content]):
    """Map temperature to Groq temperature field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform temperature into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request
        request["temperature"] = validated_value
        return request


__all__ = [
    "LanguageMapper",
    "PromptMapper",
    "TemperatureMapper",
]
