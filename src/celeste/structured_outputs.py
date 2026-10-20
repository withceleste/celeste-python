"""JSON Schema generators for structured outputs."""

from pydantic.json_schema import GenerateJsonSchema, JsonSchemaMode, JsonSchemaValue
from pydantic_core import CoreSchema


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


__all__ = ["StrictJsonSchemaGenerator"]
