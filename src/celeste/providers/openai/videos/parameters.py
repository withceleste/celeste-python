"""OpenAI Videos API parameter mappers."""

from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper


class SecondsMapper(ParameterMapper):
    """Map seconds to OpenAI seconds field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform seconds into provider request."""
        if value is None:
            return request

        # API expects string, coerce int to string
        if isinstance(value, int):
            value = str(value)

        request["seconds"] = value
        return request


class SizeMapper(ParameterMapper):
    """Map size to OpenAI size field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform size into provider request."""
        if value is None:
            return request

        request["size"] = value
        return request


class InputReferenceMapper(ParameterMapper):
    """Map input_reference to OpenAI input_reference field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform input_reference into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["input_reference"] = validated_value
        return request


__all__ = [
    "InputReferenceMapper",
    "SecondsMapper",
    "SizeMapper",
]
