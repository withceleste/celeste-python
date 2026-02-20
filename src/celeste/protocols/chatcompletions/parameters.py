"""Chat Completions protocol parameter mappers."""

import json
from typing import Any, get_origin

from pydantic import BaseModel, TypeAdapter

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.types import TextContent


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


class ResponseFormatMapper(ParameterMapper):
    """Map output_schema to Chat Completions response_format field.

    Default uses json_object mode (no schema validation server-side).
    Providers with json_schema support override map() only.
    """

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform output_schema into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["response_format"] = {"type": "json_object"}
        return request

    def parse_output(self, content: TextContent, value: object | None) -> TextContent:
        """Parse JSON string to typed output via Pydantic TypeAdapter."""
        if value is None:
            return content

        if isinstance(content, BaseModel):
            return content
        if isinstance(content, list) and content and isinstance(content[0], BaseModel):
            return content

        if isinstance(content, str):
            parsed = json.loads(content, strict=False)
        else:
            parsed = content

        origin = get_origin(value)
        if origin is list and isinstance(parsed, dict):
            if "items" in parsed:
                parsed = parsed["items"]
            else:
                parsed = list(parsed.values())

        return TypeAdapter(value).validate_python(parsed)


__all__ = ["MaxTokensMapper", "ResponseFormatMapper", "TemperatureMapper"]
