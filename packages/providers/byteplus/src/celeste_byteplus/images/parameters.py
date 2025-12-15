"""BytePlus Images API parameter mappers."""

from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper


class SizeMapper(ParameterMapper):
    """Map size to BytePlus size field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform size into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["size"] = validated_value
        return request


class WatermarkMapper(ParameterMapper):
    """Map watermark to BytePlus watermark field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform watermark into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["watermark"] = validated_value
        return request


__all__ = ["SizeMapper", "WatermarkMapper"]
