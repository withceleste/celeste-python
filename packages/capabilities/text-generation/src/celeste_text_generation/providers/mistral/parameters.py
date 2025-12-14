"""Mistral parameter mappers for text generation."""

from typing import Any, get_args, get_origin

from pydantic import BaseModel, TypeAdapter

from celeste.core import Parameter
from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste_text_generation.parameters import TextGenerationParameter


class TemperatureMapper(ParameterMapper):
    """Map temperature parameter to Mistral temperature field."""

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
    """Map max_tokens parameter to Mistral max_tokens field."""

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
    """Map thinking_budget parameter to Mistral prompt_mode.

    Maps unified thinking_budget to Mistral's prompt_mode parameter for reasoning models:
    - -1: Enable reasoning (prompt_mode: "reasoning")
    - 0: Disable reasoning (prompt_mode: null)
    - >0: Enable reasoning (prompt_mode: "reasoning") - Note: Mistral doesn't support budget control
    """

    name = TextGenerationParameter.THINKING_BUDGET

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform thinking_budget into provider request.

        Only applies to magistral reasoning models. For other models, silently ignores.
        """
        if not model.id.startswith("magistral"):
            return request

        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        if validated_value == -1:
            request["prompt_mode"] = "reasoning"
        elif validated_value == 0:
            request["prompt_mode"] = None
        else:
            request["prompt_mode"] = "reasoning"

        return request


class OutputSchemaMapper(ParameterMapper):
    """Map output_schema parameter to Mistral response_format."""

    name = TextGenerationParameter.OUTPUT_SCHEMA

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

        schema = self._convert_to_mistral_schema(validated_value)
        schema_name = self._get_schema_name(validated_value)

        request["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": schema_name,
                "description": validated_value.__doc__
                if hasattr(validated_value, "__doc__")
                else "",
                "schema": schema,
                "strict": True,
            },
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

        return TypeAdapter(value).validate_json(content)

    def _convert_to_mistral_schema(self, output_schema: Any) -> dict[str, Any]:  # noqa: ANN401
        """Convert Pydantic BaseModel or list[BaseModel] to Mistral JSON Schema format."""
        origin = get_origin(output_schema)
        if origin is list:
            inner_type = get_args(output_schema)[0]
            items_schema = inner_type.model_json_schema()
            json_schema = {"type": "array", "items": items_schema}
        else:
            json_schema = output_schema.model_json_schema()

        json_schema = self._resolve_refs(json_schema)
        return json_schema

    def _resolve_refs(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Resolve all $ref references and inline definitions for reliability."""
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

    def _get_schema_name(self, output_schema: Any) -> str:  # noqa: ANN401
        """Derive schema name from model class name."""
        origin = get_origin(output_schema)
        if origin is list:
            inner_type = get_args(output_schema)[0]
            return f"{inner_type.__name__.lower()}_list"
        else:
            return output_schema.__name__.lower()


MISTRAL_PARAMETER_MAPPERS: list[ParameterMapper] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    ThinkingBudgetMapper(),
    OutputSchemaMapper(),
]

__all__ = ["MISTRAL_PARAMETER_MAPPERS"]
