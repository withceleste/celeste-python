"""Cohere parameter mappers for text generation."""

import json
from typing import Any, get_args, get_origin

from pydantic import BaseModel, TypeAdapter

from celeste.core import Parameter
from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste_text_generation.parameters import TextGenerationParameter


class TemperatureMapper(ParameterMapper):
    """Map temperature parameter to Cohere temperature field."""

    name = Parameter.TEMPERATURE

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
    """Map max_tokens parameter to Cohere max_tokens field."""

    name = Parameter.MAX_TOKENS

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


class ThinkingBudgetMapper(ParameterMapper):
    """Map thinking_budget parameter to Cohere thinking parameter."""

    name = TextGenerationParameter.THINKING_BUDGET

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform thinking_budget into provider request.

        Maps unified thinking_budget to Cohere thinking parameter:
        - -1: Unlimited thinking ({"type": "enabled"})
        - 0: Disable thinking ({"type": "disabled"})
        - > 0: Set token budget ({"token_budget": value})
        """
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        # Map to Cohere thinking parameter format
        if validated_value == -1:
            # Unlimited thinking (default)
            request["thinking"] = {"type": "enabled"}
        elif validated_value == 0:
            # Disable thinking
            request["thinking"] = {"type": "disabled"}
        else:
            # Set token budget
            request["thinking"] = {"token_budget": validated_value}

        return request


class OutputSchemaMapper(ParameterMapper):
    """Map output_schema parameter to Cohere response_format."""

    name = TextGenerationParameter.OUTPUT_SCHEMA

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform output_schema into provider request.

        Converts Pydantic BaseModel or list[BaseModel] to Cohere JSON Schema format.
        Sets request["response_format"] = {"type": "json_object", "schema": {...}}.
        """
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        schema = self._convert_to_cohere_schema(validated_value)
        request["response_format"] = {
            "type": "json_object",
            "schema": schema,
        }

        return request

    def parse_output(self, content: str, value: object | None) -> str | BaseModel:
        """Parse JSON string to BaseModel instance if output_schema provided.

        Args:
            content: Raw text content (JSON string when output_schema is set).
            value: Original output_schema parameter value.

        Returns:
            BaseModel instance if value provided, otherwise str unchanged.
        """
        if value is None:
            return content

        # Parse JSON string first
        parsed_json = json.loads(content)

        # For list[T] models, unwrap the items wrapper (Cohere wraps arrays in {"items": [...]})
        origin = get_origin(value)
        if origin is list and isinstance(parsed_json, dict) and "items" in parsed_json:
            parsed_json = parsed_json["items"]

        # Parse to BaseModel instance using TypeAdapter
        # TypeAdapter handles both Person and list[Person]
        return TypeAdapter(value).validate_json(json.dumps(parsed_json))

    def _convert_to_cohere_schema(self, output_schema: Any) -> dict[str, Any]:  # noqa: ANN401
        """Convert Pydantic BaseModel or list[BaseModel] to Cohere JSON Schema format.

        Cohere requires flattened schemas without $ref/$defs.
        For list[T] models, wraps array schema in object with items property.
        """
        origin = get_origin(output_schema)
        if origin is list:
            # For list[T], wrap array schema in object wrapper
            inner_type = get_args(output_schema)[0]
            items_schema = inner_type.model_json_schema()
            json_schema = {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": items_schema,
                    }
                },
                "required": ["items"],
            }
        else:
            # For BaseModel, use model_json_schema directly
            json_schema = output_schema.model_json_schema()

        # Resolve $ref references inline (Cohere requires flattened schemas)
        json_schema = self._resolve_refs(json_schema)

        return json_schema

    def _resolve_refs(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Resolve all $ref references and inline definitions (Cohere requires flattened schemas).

        This method:
        1. Collects all $defs dictionaries from the schema tree
        2. Removes $defs keys from the schema
        3. Replaces $ref references with inlined definitions
        4. Recursively processes nested objects/arrays
        """
        defs: dict[str, Any] = {}

        def collect_defs(value: object) -> None:
            """Recursively collect all $defs dictionaries."""
            if isinstance(value, dict):
                if "$defs" in value:
                    defs.update(value["$defs"])
                for v in value.values():
                    collect_defs(v)
            elif isinstance(value, list):
                for item in value:
                    collect_defs(item)

        collect_defs(schema)

        def remove_defs(value: object) -> object:
            """Recursively remove all $defs keys."""
            if isinstance(value, dict):
                result = {k: remove_defs(v) for k, v in value.items() if k != "$defs"}
                return result
            elif isinstance(value, list):
                return [remove_defs(item) for item in value]
            return value

        schema = remove_defs(schema)

        def resolve(value: object) -> object:
            """Recursively resolve $ref references in schema."""
            if isinstance(value, dict):
                if "$ref" in value:
                    ref_path = value["$ref"]
                    if ref_path.startswith("#/$defs/"):
                        ref_name = ref_path.split("/")[-1]
                        if ref_name in defs:
                            resolved = defs[ref_name].copy()
                            # Merge any additional properties from the $ref object
                            resolved.update(
                                {k: v for k, v in value.items() if k != "$ref"}
                            )
                            return resolve(resolved)
                return {k: resolve(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [resolve(item) for item in value]
            return value

        return resolve(schema)


COHERE_PARAMETER_MAPPERS: list[ParameterMapper] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    ThinkingBudgetMapper(),
    OutputSchemaMapper(),
]

__all__ = ["COHERE_PARAMETER_MAPPERS"]
