"""JSON Schema generators for structured outputs."""

import json
from typing import get_origin

from pydantic import BaseModel, TypeAdapter
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaMode, JsonSchemaValue
from pydantic_core import CoreSchema

from celeste.types import OutputSchema, TextContent


class StrictJsonSchemaGenerator(GenerateJsonSchema):
    """Forces additionalProperties: false and all properties required on objects (OpenAI, Anthropic, xAI)."""

    def generate(
        self, schema: CoreSchema, mode: JsonSchemaMode = "validation"
    ) -> JsonSchemaValue:
        json_schema = super().generate(schema, mode=mode)
        self._add_strict_props(json_schema)
        return json_schema

    def _add_strict_props(self, schema: dict) -> None:
        if not isinstance(schema, dict):
            return
        if schema.get("type") == "object" and "additionalProperties" not in schema:
            schema["additionalProperties"] = False
        if "properties" in schema:
            schema["required"] = list(schema["properties"])
        for key in ("properties", "$defs", "items", "allOf", "anyOf", "oneOf"):
            if key in schema:
                if isinstance(schema[key], dict):
                    for v in schema[key].values():
                        self._add_strict_props(v)
                elif isinstance(schema[key], list):
                    for item in schema[key]:
                        self._add_strict_props(item)


def parse_json_output(content: TextContent, value: OutputSchema | None) -> TextContent:
    """Parse JSON text to the schema; a list schema unwraps {"items": [...]} or dict values."""
    if value is None or content == "":
        return content

    if isinstance(content, BaseModel):
        return content
    if isinstance(content, list) and content and isinstance(content[0], BaseModel):
        return content

    parsed = json.loads(content, strict=False) if isinstance(content, str) else content

    if get_origin(value) is list and isinstance(parsed, dict):
        parsed = parsed["items"] if "items" in parsed else list(parsed.values())

    return TypeAdapter(value).validate_python(parsed)


__all__ = ["StrictJsonSchemaGenerator", "parse_json_output"]
