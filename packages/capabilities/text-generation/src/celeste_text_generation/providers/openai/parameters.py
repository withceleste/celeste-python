"""OpenAI parameter mappers for text generation."""

import json
from typing import Any, get_args, get_origin

from pydantic import BaseModel, TypeAdapter

from celeste.core import Parameter
from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste_text_generation.parameters import TextGenerationParameter


class OutputSchemaMapper(ParameterMapper):
    """Map output_schema parameter to OpenAI text.format."""

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

        schema = self._convert_to_openai_schema(validated_value)
        schema_name = self._get_schema_name(validated_value)

        request.setdefault("text", {})["format"] = {
            "type": "json_schema",
            "name": schema_name,
            "strict": True,
            "schema": schema,
        }

        return request

    def parse_output(self, content: str, value: object | None) -> str | BaseModel:
        """Parse JSON string to BaseModel instance if output_schema provided."""
        if value is None:
            return content

        parsed_json = json.loads(content)
        origin = get_origin(value)
        if origin is list and isinstance(parsed_json, dict) and "items" in parsed_json:
            parsed_json = parsed_json["items"]

        return TypeAdapter(value).validate_json(json.dumps(parsed_json))

    def _convert_to_openai_schema(self, output_schema: Any) -> dict[str, Any]:  # noqa: ANN401
        """Convert Pydantic BaseModel or list[BaseModel] to OpenAI JSON Schema format."""
        origin = get_origin(output_schema)
        if origin is list:
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
            json_schema = output_schema.model_json_schema()

        json_schema = self._transform_schema_for_openai(json_schema)
        return json_schema

    def _transform_schema_for_openai(
        self, schema: dict[str, Any], defs: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Recursively transform schema for OpenAI Responses API."""
        if not isinstance(schema, dict):
            return schema

        if defs is None:
            defs = self._collect_all_defs(schema)

        if "$ref" in schema:
            ref_path = schema["$ref"]
            if ref_path.startswith("#/$defs/"):
                def_name = ref_path.split("/")[-1]
                if def_name in defs:
                    expanded = defs[def_name].copy()
                    expanded.pop("description", None)
                    return self._transform_schema_for_openai(expanded, defs)
            return schema

        result: dict[str, Any] = {}
        for key, value in schema.items():
            if key == "$defs":
                continue
            elif isinstance(value, dict):
                result[key] = self._transform_schema_for_openai(value, defs)
            elif isinstance(value, list):
                result[key] = [
                    self._transform_schema_for_openai(item, defs)
                    if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                result[key] = value

        if result.get("type") == "object":
            result["additionalProperties"] = False

        return result

    def _collect_all_defs(self, schema: Any) -> dict[str, Any]:  # noqa: ANN401
        """Recursively collect all $defs dictionaries from schema tree."""
        defs: dict[str, Any] = {}

        def collect(value: Any) -> None:  # noqa: ANN401
            if isinstance(value, dict):
                if "$defs" in value:
                    defs.update(value["$defs"])
                for v in value.values():
                    collect(v)
            elif isinstance(value, list):
                for item in value:
                    collect(item)

        collect(schema)
        return defs

    def _get_schema_name(self, output_schema: Any) -> str:  # noqa: ANN401
        """Derive schema name from model class name."""
        origin = get_origin(output_schema)
        if origin is list:
            inner_type = get_args(output_schema)[0]
            class_name = inner_type.__name__
            return f"{class_name.lower()}_list"
        else:
            return output_schema.__name__.lower()


class TemperatureMapper(ParameterMapper):
    """Map temperature parameter to OpenAI temperature field."""

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
    """Map max_tokens parameter to OpenAI max_output_tokens field."""

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

        request["max_output_tokens"] = validated_value
        return request


class ThinkingBudgetMapper(ParameterMapper):
    """Map thinking_budget parameter to OpenAI reasoning.effort field."""

    name = TextGenerationParameter.THINKING_BUDGET

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform thinking_budget into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request.setdefault("reasoning", {})["effort"] = validated_value
        return request


class VerbosityMapper(ParameterMapper):
    """Map verbosity parameter to OpenAI text.verbosity field."""

    name = TextGenerationParameter.VERBOSITY

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform verbosity into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request.setdefault("text", {})["verbosity"] = validated_value
        return request


OPENAI_PARAMETER_MAPPERS: list[ParameterMapper] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    ThinkingBudgetMapper(),
    VerbosityMapper(),
    OutputSchemaMapper(),
]

__all__ = ["OPENAI_PARAMETER_MAPPERS"]
