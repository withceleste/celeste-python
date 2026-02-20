"""Chat Completions protocol parameter mappers."""

from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper


class TemperatureMapper(ParameterMapper):
    """Map temperature to Chat Completions temperature field."""

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


class MaxTokensMapper(ParameterMapper):
    """Map max_tokens to Chat Completions max_tokens field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform max_tokens into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["max_tokens"] = validated_value
        return request


__all__ = ["MaxTokensMapper", "TemperatureMapper"]
