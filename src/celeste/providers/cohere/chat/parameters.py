"""Cohere Chat API parameter mappers."""

import json
from typing import Any, get_args, get_origin

from pydantic import BaseModel, TypeAdapter

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.structured_outputs import RefResolvingJsonSchemaGenerator
from celeste.types import TextContent


class TemperatureMapper(ParameterMapper):
    """Map temperature to Cohere temperature field."""

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
    """Map max_tokens to Cohere max_tokens field."""

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


class ThinkingMapper(ParameterMapper):
    """Map thinking to Cohere thinking field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform thinking into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        if validated_value == "enabled":
            request["thinking"] = {"type": "enabled"}
        elif validated_value == "disabled":
            request["thinking"] = {"type": "disabled"}
        else:
            request["thinking"] = {"type": "enabled", "token_budget": validated_value}
        return request


class ResponseFormatMapper(ParameterMapper):
    """Map output_schema to Cohere response_format field.

    Handles both single BaseModel and list[BaseModel] types.
    Cohere requires top-level object, so lists are wrapped in {items: []}.
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

        origin = get_origin(validated_value)
        if origin is list:
            # Cohere requires top-level object, wrap list in {items: [...]}
            inner_type = get_args(validated_value)[0]
            inner_schema = TypeAdapter(inner_type).json_schema(
                schema_generator=RefResolvingJsonSchemaGenerator,
                mode="serialization",
            )
            schema = {
                "type": "object",
                "properties": {"items": {"type": "array", "items": inner_schema}},
                "required": ["items"],
            }
        else:
            schema = TypeAdapter(validated_value).json_schema(
                schema_generator=RefResolvingJsonSchemaGenerator,
                mode="serialization",
            )

        request["response_format"] = {
            "type": "json_object",
            "schema": schema,
        }
        return request

    def parse_output(self, content: TextContent, value: object | None) -> TextContent:
        """Parse JSON to BaseModel using Pydantic's TypeAdapter."""
        if value is None:
            return content

        # If content is already a BaseModel, return it unchanged
        if isinstance(content, BaseModel):
            return content
        if isinstance(content, list) and content and isinstance(content[0], BaseModel):
            return content

        if isinstance(content, str):
            parsed = json.loads(content)
        else:
            parsed = content

        # Unwrap list from items wrapper
        origin = get_origin(value)
        if origin is list and isinstance(parsed, dict) and "items" in parsed:
            parsed = parsed["items"]

        return TypeAdapter(value).validate_python(parsed)


__all__ = [
    "MaxTokensMapper",
    "ResponseFormatMapper",
    "TemperatureMapper",
    "ThinkingMapper",
]
