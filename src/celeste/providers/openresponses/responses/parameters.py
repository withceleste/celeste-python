"""OpenResponses API parameter mappers."""

import json
from typing import Any, get_args, get_origin

from pydantic import BaseModel, TypeAdapter

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.structured_outputs import StrictJsonSchemaGenerator
from celeste.types import TextContent


class TemperatureMapper(ParameterMapper):
    """Map temperature to Responses temperature field."""

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


class MaxOutputTokensMapper(ParameterMapper):
    """Map max_tokens to Responses max_output_tokens field."""

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

        request["max_output_tokens"] = validated_value
        return request


class TextFormatMapper(ParameterMapper):
    """Map output_schema to Responses text.format field.

    Handles both single BaseModel and list[BaseModel] types.
    Responses requires top-level object, so list types are wrapped.
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
            inner_type = get_args(validated_value)[0]
            inner_schema = TypeAdapter(inner_type).json_schema(
                schema_generator=StrictJsonSchemaGenerator,
                mode="serialization",
            )
            schema = {
                "type": "object",
                "properties": {"items": {"type": "array", "items": inner_schema}},
                "required": ["items"],
                "additionalProperties": False,
            }
            name = f"{inner_type.__name__.lower()}_list"
        else:
            schema = TypeAdapter(validated_value).json_schema(
                schema_generator=StrictJsonSchemaGenerator,
                mode="serialization",
            )
            name = validated_value.__name__.lower()

        request.setdefault("text", {})["format"] = {
            "type": "json_schema",
            "name": name,
            "schema": schema,
            "strict": True,
        }
        return request

    def parse_output(self, content: TextContent, value: object | None) -> TextContent:
        """Parse JSON string to BaseModel using Pydantic's TypeAdapter."""
        if value is None:
            return content

        if isinstance(content, BaseModel):
            return content
        if isinstance(content, list) and content and isinstance(content[0], BaseModel):
            return content

        if isinstance(content, str):
            parsed = json.loads(content)
        else:
            parsed = content

        origin = get_origin(value)
        if origin is list and isinstance(parsed, dict) and "items" in parsed:
            parsed = parsed["items"]

        return TypeAdapter(value).validate_python(parsed)


__all__ = [
    "MaxOutputTokensMapper",
    "TemperatureMapper",
    "TextFormatMapper",
]
