"""Google parameter mappers for text generation."""

from typing import Any, get_args, get_origin

from pydantic import BaseModel, TypeAdapter

from celeste.core import Parameter
from celeste.mime_types import ApplicationMimeType
from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste_text_generation.parameters import TextGenerationParameter


class TemperatureMapper(ParameterMapper):
    """Map temperature parameter to Google generationConfig."""

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

        request.setdefault("generationConfig", {})["temperature"] = validated_value
        return request


class MaxTokensMapper(ParameterMapper):
    """Map max_tokens parameter to Google generationConfig.maxOutputTokens."""

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

        request.setdefault("generationConfig", {})["maxOutputTokens"] = validated_value
        return request


class ThinkingBudgetMapper(ParameterMapper):
    """Map thinking_budget parameter to Google generationConfig.thinkingConfig.thinkingBudget."""

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

        request.setdefault("generationConfig", {}).setdefault("thinkingConfig", {})[
            "thinkingBudget"
        ] = validated_value
        return request


class ThinkingLevelMapper(ParameterMapper):
    """Map thinking_level parameter to Google generationConfig.thinkingConfig.thinkingLevel."""

    name = TextGenerationParameter.THINKING_LEVEL

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform thinking_level into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request.setdefault("generationConfig", {}).setdefault("thinkingConfig", {})[
            "thinkingLevel"
        ] = validated_value
        return request


class OutputSchemaMapper(ParameterMapper):
    """Map output_schema parameter to Google generationConfig.responseSchema."""

    name = TextGenerationParameter.OUTPUT_SCHEMA

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform response_model into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        schema = self._convert_to_google_schema(validated_value)

        config = request.setdefault("generationConfig", {})
        config["responseSchema"] = schema
        config["responseMimeType"] = ApplicationMimeType.JSON

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

    def _convert_to_google_schema(self, output_schema: Any) -> dict[str, Any]:  # noqa: ANN401
        """Convert Pydantic BaseModel or list[BaseModel] to Google OpenAPI 3.0 format."""
        origin = get_origin(output_schema)
        if origin is list:
            inner_type = get_args(output_schema)[0]
            items_schema = inner_type.model_json_schema()
            json_schema = {"type": "array", "items": items_schema}
        else:
            json_schema = output_schema.model_json_schema()

        json_schema = self._resolve_refs(json_schema)
        json_schema = self._remove_unsupported_fields(json_schema)
        return self._uppercase_types(json_schema)

    def _uppercase_types(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Recursively uppercase all 'type' field values in schema."""
        result: dict[str, Any] = {}

        for key, value in schema.items():
            if key == "type" and isinstance(value, str):
                result[key] = value.upper()
            elif isinstance(value, dict):
                result[key] = self._uppercase_types(value)
            elif isinstance(value, list):
                result[key] = [
                    self._uppercase_types(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                result[key] = value

        return result

    def _resolve_refs(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Resolve all $ref references and inline definitions (Google API doesn't support $ref)."""
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
                            resolved.update(
                                {k: v for k, v in value.items() if k != "$ref"}
                            )
                            return resolve(resolved)
                return {k: resolve(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [resolve(item) for item in value]
            return value

        return resolve(schema)

    def _remove_unsupported_fields(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Remove unsupported fields from schema (e.g., 'title' that Google API doesn't accept)."""
        result: dict[str, Any] = {}

        for key, value in schema.items():
            if key == "title":
                continue

            if isinstance(value, dict):
                result[key] = self._remove_unsupported_fields(value)
            elif isinstance(value, list):
                result[key] = [
                    self._remove_unsupported_fields(item)
                    if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                result[key] = value

        return result


GOOGLE_PARAMETER_MAPPERS: list[ParameterMapper] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    ThinkingBudgetMapper(),
    ThinkingLevelMapper(),
    OutputSchemaMapper(),
]

__all__ = ["GOOGLE_PARAMETER_MAPPERS"]
