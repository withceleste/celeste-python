"""Anthropic parameter mappers."""

import json
from enum import StrEnum
from typing import Any, get_args, get_origin

from pydantic import BaseModel, TypeAdapter

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste_text_generation.parameters import TextGenerationParameter


class ThinkingBudgetMapper(ParameterMapper):
    """Map thinking_budget parameter to Anthropic thinking.budget_tokens."""

    name: StrEnum = TextGenerationParameter.THINKING_BUDGET

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
            ValueError: If value is not -1 and is less than 1024 (minimum required).
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
                raise ValueError(msg)
            thinking_config = {"type": "enabled", "budget_tokens": validated_value}

        request["thinking"] = thinking_config
        return request


class OutputSchemaMapper(ParameterMapper):
    """Map output_schema parameter to Anthropic tools parameter (tool-based structured output)."""

    name: StrEnum = TextGenerationParameter.OUTPUT_SCHEMA

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform output_schema into provider request.

        Converts unified output_schema to Anthropic tools parameter:
        - Creates a single tool definition with input_schema matching the output schema
        - Sets tool_choice to force tool use
        - Handles both BaseModel and list[BaseModel] types

        Args:
            request: Provider request dict.
            value: output_schema value (type[BaseModel] | None).
            model: Model instance containing parameter_constraints for validation.
            model: Model instance with parameter constraints for validation.

        Returns:
            Updated request dict with tools and tool_choice if value provided.
        """
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        # Convert Pydantic model to JSON Schema
        schema = self._convert_to_anthropic_schema(validated_value)
        tool_name = self._get_tool_name(validated_value)

        # Create tool definition with input_schema matching output schema
        tool_def = {
            "name": tool_name,
            "description": f"Extract structured data conforming to {self._get_schema_description(validated_value)}",
            "input_schema": schema,
        }

        # Add tools array to request
        request["tools"] = [tool_def]

        # Force tool use by setting tool_choice
        request["tool_choice"] = {"type": "tool", "name": tool_name}

        return request

    def parse_output(
        self, content: str | dict[str, Any], value: object | None
    ) -> str | BaseModel:
        """Parse tool_use blocks from response to BaseModel instance.

        Extracts structured data from tool_use.input field and converts to BaseModel.
        For list[BaseModel], extracts the "items" array from the wrapped object.

        Args:
            content: Either tool_use.input dict (from tool_use block) or JSON string.
            value: Original output_schema parameter value.

        Returns:
            BaseModel instance if value provided, otherwise str unchanged.
        """
        if value is None:
            return content if isinstance(content, str) else json.dumps(content)

        # If content is already a dict (from tool_use.input), use it directly
        if isinstance(content, dict):
            parsed_json = content
        else:
            # Otherwise parse as JSON string
            parsed_json = json.loads(content)

        # Check if value is list[BaseModel] and content is wrapped in object
        origin = get_origin(value)
        if origin is list:
            # Handle empty dict case FIRST - convert to empty array before checking for "items"
            if isinstance(parsed_json, dict) and not parsed_json:
                # Empty dict when expecting list - convert to empty array
                parsed_json = []
            elif isinstance(parsed_json, dict) and "items" in parsed_json:
                # Extract items array from wrapped format
                parsed_json = parsed_json["items"]
            # If it's already an array (backward compatibility), use it directly
            # parsed_json is now the array, ready for TypeAdapter
        elif isinstance(parsed_json, dict) and not parsed_json:
            # Empty dict for BaseModel (not list) - this is invalid, raise error
            msg = "Empty tool_use input dict cannot be converted to BaseModel"
            raise ValueError(msg)

        # Parse to BaseModel instance using TypeAdapter
        # TypeAdapter handles both BaseModel and list[BaseModel]
        return TypeAdapter(value).validate_json(json.dumps(parsed_json))

    def _convert_to_anthropic_schema(self, output_schema: Any) -> dict[str, Any]:  # noqa: ANN401
        """Convert Pydantic BaseModel or list[BaseModel] to Anthropic JSON Schema format.

        Anthropic requires input_schema to always be an object type.
        For list[T], wraps array schema in an object with "items" property.

        Args:
            output_schema: Pydantic BaseModel class or list[BaseModel] type.

        Returns:
            JSON Schema dictionary compatible with Anthropic (always object type).
        """
        origin = get_origin(output_schema)
        if origin is list:
            # For list[T], wrap array schema in an object (Anthropic requirement)
            inner_type = get_args(output_schema)[0]
            items_schema = inner_type.model_json_schema()
            # Resolve refs in items schema first
            items_schema = self._resolve_refs(items_schema)
            # Wrap in object with "items" property
            json_schema = {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": items_schema,
                    },
                },
                "required": ["items"],
            }
        else:
            # For BaseModel, use model_json_schema directly
            json_schema = output_schema.model_json_schema()
            # Resolve $ref references inline (Anthropic may not support $ref)
            json_schema = self._resolve_refs(json_schema)

        return json_schema

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

    def _get_tool_name(self, output_schema: Any) -> str:  # noqa: ANN401
        """Derive tool name from model class name.

        Args:
            output_schema: Pydantic BaseModel class or list[BaseModel] type.

        Returns:
            Tool name (lowercase class name or "extract_data" as fallback).
        """
        origin = get_origin(output_schema)
        if origin is list:
            inner_type = get_args(output_schema)[0]
            return inner_type.__name__.lower() or "extract_data"
        return output_schema.__name__.lower() or "extract_data"

    def _get_schema_description(self, output_schema: Any) -> str:  # noqa: ANN401
        """Get description for tool definition.

        Args:
            output_schema: Pydantic BaseModel class or list[BaseModel] type.

        Returns:
            Schema description string.
        """
        origin = get_origin(output_schema)
        if origin is list:
            inner_type = get_args(output_schema)[0]
            return f"array of {inner_type.__name__}"
        return output_schema.__name__


ANTHROPIC_PARAMETER_MAPPERS: list[ParameterMapper] = [
    ThinkingBudgetMapper(),
    OutputSchemaMapper(),
]

__all__ = ["ANTHROPIC_PARAMETER_MAPPERS"]
