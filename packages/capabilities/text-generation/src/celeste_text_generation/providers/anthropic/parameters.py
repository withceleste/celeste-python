"""Anthropic parameter mappers for text generation."""

import json
from typing import Any, get_args, get_origin

from pydantic import BaseModel, TypeAdapter

from celeste.exceptions import ConstraintViolationError
from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste_text_generation.parameters import TextGenerationParameter


class ThinkingBudgetMapper(ParameterMapper):
    """Map thinking_budget parameter to Anthropic thinking.budget_tokens."""

    name = TextGenerationParameter.THINKING_BUDGET

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform thinking_budget into provider request.

        Maps unified thinking_budget to Anthropic thinking parameter:
        - thinking_budget=None → No thinking parameter (thinking disabled)
        - thinking_budget=-1 → {"type": "auto"} (dynamic budget, automatic)
        - thinking_budget=N (where N >= 1024) → {"type": "enabled", "budget_tokens": N} (fixed budget)

        Args:
            request: Provider request dict.
            value: thinking_budget value (int | None).
            model: Model instance containing parameter_constraints for validation.
            model: Model instance with parameter constraints for validation.

        Returns:
            Updated request dict with thinking parameter if value provided.

        Raises:
            ConstraintViolationError: If value is not -1 and is less than 1024 (minimum required).
        """
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        # Build thinking parameter object
        if validated_value == -1:
            # Dynamic thinking: use "auto" type (no budget_tokens)
            thinking_config: dict[str, Any] = {"type": "auto"}
        else:
            # Fixed budget: validate minimum is 1024
            if validated_value < 1024:
                msg = f"thinking_budget must be -1 (dynamic) or >= 1024 for {model.id}, got {validated_value}"
                raise ConstraintViolationError(msg)
            thinking_config = {"type": "enabled", "budget_tokens": validated_value}

        request["thinking"] = thinking_config
        return request


class OutputSchemaMapper(ParameterMapper):
    """Map output_schema parameter to Anthropic native structured outputs (output_format)."""

    name = TextGenerationParameter.OUTPUT_SCHEMA

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform output_schema into provider request using native structured outputs.

        Converts unified output_schema to Anthropic output_format parameter:
        - Uses output_format with type: "json_schema" and schema definition
        - Handles both BaseModel and list[BaseModel] types
        - For list[BaseModel], schema is array type directly

        Args:
            request: Provider request dict.
            value: output_schema value (type[BaseModel] | None).
            model: Model instance containing parameter_constraints for validation.

        Returns:
            Updated request dict with output_format if value provided.
        """
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        schema = self._convert_to_json_schema(validated_value)

        request["output_format"] = {
            "type": "json_schema",
            "schema": schema,
        }

        return request

    def parse_output(
        self, content: str | dict[str, Any], value: object | None
    ) -> str | BaseModel:
        """Parse JSON text from response to BaseModel instance.

        With native structured outputs, content is direct JSON text in content[0].text.
        For list[BaseModel], content is array directly.

        Args:
            content: JSON string from content[0].text.
            value: Original output_schema parameter value.

        Returns:
            BaseModel instance if value provided, otherwise str unchanged.
        """
        if value is None:
            return content if isinstance(content, str) else json.dumps(content)

        if isinstance(content, dict):
            parsed_json = content
        else:
            parsed_json = json.loads(content)

        return TypeAdapter(value).validate_json(json.dumps(parsed_json))

    def _convert_to_json_schema(self, output_schema: Any) -> dict[str, Any]:  # noqa: ANN401
        """Convert Pydantic BaseModel or list[BaseModel] to JSON Schema format.

        For native structured outputs, list[T] is array type directly.
        Ensures all object types have additionalProperties: false as required by Anthropic.

        Args:
            output_schema: Pydantic BaseModel class or list[BaseModel] type.

        Returns:
            JSON Schema dictionary compatible with Anthropic structured outputs.
        """
        origin = get_origin(output_schema)
        if origin is list:
            inner_type = get_args(output_schema)[0]
            items_schema = inner_type.model_json_schema()
            items_schema = self._resolve_refs(items_schema)
            json_schema = {
                "type": "array",
                "items": items_schema,
            }
        else:
            json_schema = output_schema.model_json_schema()
            json_schema = self._resolve_refs(json_schema)

        json_schema = self._ensure_additional_properties(json_schema)
        return json_schema

    def _ensure_additional_properties(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Ensure all object types have additionalProperties: false."""
        if not isinstance(schema, dict):
            return schema

        schema = schema.copy()

        if schema.get("type") == "object":
            schema["additionalProperties"] = False

        for key in ["properties", "items"]:
            if key in schema:
                if key == "properties":
                    schema[key] = {
                        k: self._ensure_additional_properties(v)
                        for k, v in schema[key].items()
                    }
                else:
                    schema[key] = self._ensure_additional_properties(schema[key])

        for key in ["anyOf", "allOf"]:
            if key in schema:
                schema[key] = [
                    self._ensure_additional_properties(item) for item in schema[key]
                ]

        return schema

    def _resolve_refs(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Resolve all $ref references and inline definitions.

        Args:
            schema: JSON Schema dictionary potentially containing $ref.

        Returns:
            Schema with $ref references resolved inline.
        """
        defs: dict[str, Any] = {}

        def collect_defs(value: Any) -> None:  # noqa: ANN401
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

        def remove_defs(value: Any) -> Any:  # noqa: ANN401
            """Recursively remove all $defs keys."""
            if isinstance(value, dict):
                result = {k: remove_defs(v) for k, v in value.items() if k != "$defs"}
                return result
            elif isinstance(value, list):
                return [remove_defs(item) for item in value]
            return value

        schema = remove_defs(schema)

        def resolve(value: Any) -> Any:  # noqa: ANN401
            """Recursively resolve $ref references in schema."""
            if isinstance(value, dict):
                if "$ref" in value:
                    ref_path = value["$ref"]
                    if ref_path.startswith("#/$defs/"):
                        ref_name = ref_path.split("/")[-1]
                        if ref_name in defs:
                            resolved = defs[ref_name].copy()
                            resolved.update(
                                {k: v for k, v in value.items() if k != "$ref"}
                            )
                            return resolve(resolved)
                return {k: resolve(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [resolve(item) for item in value]
            return value

        return resolve(schema)


ANTHROPIC_PARAMETER_MAPPERS: list[ParameterMapper] = [
    ThinkingBudgetMapper(),
    OutputSchemaMapper(),
]

__all__ = ["ANTHROPIC_PARAMETER_MAPPERS"]
