"""Groq Chat API parameter mappers."""

import json
from typing import Any, get_args, get_origin

from pydantic import BaseModel, TypeAdapter

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.structured_outputs import StrictJsonSchemaGenerator
from celeste.types import TextContent


class ResponseFormatMapper(ParameterMapper):
    """Map output_schema to Groq response_format field (json_schema mode).

    Handles both single BaseModel and list[BaseModel] types.
    Groq requires top-level object, so lists are wrapped in {items: []}.
    Uses json_schema mode with strict: false for Llama 4 models.
    """

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform output_schema into Groq response_format."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        origin = get_origin(validated_value)
        if origin is list:
            # Groq requires top-level object, wrap list in {"items": [...]}
            inner_type = get_args(validated_value)[0]
            inner_schema = TypeAdapter(inner_type).json_schema(
                schema_generator=StrictJsonSchemaGenerator,
                mode="serialization",
            )
            schema = {
                "type": "object",
                "properties": {"items": {"type": "array", "items": inner_schema}},
                "required": ["items"],
            }
            name = f"{inner_type.__name__.lower()}_list"
        else:
            schema = TypeAdapter(validated_value).json_schema(
                schema_generator=StrictJsonSchemaGenerator,
                mode="serialization",
            )
            name = validated_value.__name__.lower()

        request["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": name,
                "strict": False,  # Groq requires strict: false for Llama 4
                "schema": schema,
            },
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

        parsed_json = (
            json.loads(content, strict=False) if isinstance(content, str) else content
        )

        # Unwrap list from items wrapper
        origin = get_origin(value)
        if origin is list and isinstance(parsed_json, dict) and "items" in parsed_json:
            parsed_json = parsed_json["items"]

        return TypeAdapter(value).validate_python(parsed_json)


__all__ = ["ResponseFormatMapper"]
