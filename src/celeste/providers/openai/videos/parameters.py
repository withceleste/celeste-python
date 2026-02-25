"""OpenAI Videos API parameter mappers."""

from typing import Any

from celeste.models import Model
from celeste.parameters import FieldMapper, ParameterMapper
from celeste.types import VideoContent


class SecondsMapper(ParameterMapper[VideoContent]):
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


class SizeMapper(ParameterMapper[VideoContent]):
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


class InputReferenceMapper(FieldMapper[VideoContent]):
    """Map input_reference to OpenAI input_reference field."""

    field = "input_reference"


__all__ = [
    "InputReferenceMapper",
    "SecondsMapper",
    "SizeMapper",
]
