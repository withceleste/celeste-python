"""JSON Schema generators for structured outputs."""

from typing import Any

from pydantic.json_schema import GenerateJsonSchema, JsonSchemaMode, JsonSchemaValue
from pydantic_core import CoreSchema


class StrictJsonSchemaGenerator(GenerateJsonSchema):
    """Adds additionalProperties: false to all objects (OpenAI, Anthropic, xAI)."""

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
        for key in ("properties", "$defs", "items", "allOf", "anyOf", "oneOf"):
            if key in schema:
                if isinstance(schema[key], dict):
                    for v in schema[key].values():
                        self._add_strict_props(v)
                elif isinstance(schema[key], list):
                    for item in schema[key]:
                        self._add_strict_props(item)


class RefResolvingJsonSchemaGenerator(GenerateJsonSchema):
    """Resolves $ref references inline (Cohere - doesn't support $defs)."""

    def generate(
        self, schema: CoreSchema, mode: JsonSchemaMode = "validation"
    ) -> JsonSchemaValue:
        json_schema = super().generate(schema, mode=mode)
        self._resolve_refs(json_schema)
        return json_schema

    def _resolve_refs(self, schema: dict) -> None:
        if not isinstance(schema, dict):
            return
        defs = schema.pop("$defs", {})
        if not defs:
            return

        def resolve(obj: Any) -> Any:  # noqa: ANN401
            if isinstance(obj, dict):
                if "$ref" in obj:
                    ref_path = obj["$ref"]
                    if ref_path.startswith("#/$defs/"):
                        ref_name = ref_path.split("/")[-1]
                        if ref_name in defs:
                            resolved = defs[ref_name].copy()
                            resolved.update(
                                {k: v for k, v in obj.items() if k != "$ref"}
                            )
                            return resolve(resolved)
                return {k: resolve(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [resolve(item) for item in obj]
            return obj

        for key in list(schema.keys()):
            schema[key] = resolve(schema[key])


class StrictRefResolvingJsonSchemaGenerator(
    StrictJsonSchemaGenerator, RefResolvingJsonSchemaGenerator
):
    """Adds strict props AND resolves refs (Mistral - $defs support unconfirmed)."""

    def generate(
        self, schema: CoreSchema, mode: JsonSchemaMode = "validation"
    ) -> JsonSchemaValue:
        json_schema = GenerateJsonSchema.generate(self, schema, mode=mode)
        self._add_strict_props(json_schema)
        self._resolve_refs(json_schema)
        return json_schema


__all__ = [
    "RefResolvingJsonSchemaGenerator",
    "StrictJsonSchemaGenerator",
    "StrictRefResolvingJsonSchemaGenerator",
]
