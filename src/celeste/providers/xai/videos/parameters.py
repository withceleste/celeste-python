"""xAI Videos API parameter mappers."""

from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper


class DurationMapper(ParameterMapper):
    """Map duration to xAI duration field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform duration into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["duration"] = validated_value
        return request


class AspectRatioMapper(ParameterMapper):
    """Map aspect_ratio to xAI aspect_ratio field."""

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

        request["aspect_ratio"] = validated_value
        return request


class ResolutionMapper(ParameterMapper):
    """Map resolution to xAI resolution field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform resolution into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["resolution"] = validated_value
        return request


__all__ = [
    "AspectRatioMapper",
    "DurationMapper",
    "ResolutionMapper",
]
