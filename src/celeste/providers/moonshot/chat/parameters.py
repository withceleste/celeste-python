"""Moonshot Chat API parameter mappers."""

import json
from typing import Any, get_origin

from pydantic import BaseModel, TypeAdapter

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.types import TextContent


class ResponseFormatMapper(ParameterMapper):
    """Map output_schema to Moonshot response_format field.

    Moonshot supports basic JSON mode only (no schema validation server-side).
    Schema validation happens client-side via parse_output method.
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
        """Parse JSON to BaseModel using Pydantic's TypeAdapter."""
        if value is None:
            return content

        # If content is already a BaseModel, return it unchanged
        if isinstance(content, BaseModel):
            return content
        if isinstance(content, list) and content and isinstance(content[0], BaseModel):
            return content

        if isinstance(content, str):
            parsed = json.loads(content, strict=False)
        else:
            parsed = content

        # For list[T], handle various formats Moonshot might return
        origin = get_origin(value)
        if origin is list and isinstance(parsed, dict):
            if "items" in parsed:
                parsed = parsed["items"]
            else:
                parsed = list(parsed.values())

        return TypeAdapter(value).validate_python(parsed)


__all__ = ["ResponseFormatMapper"]
