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
    """Map output_schema parameter to Google generationConfig.responseJsonSchema."""

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
        config["responseJsonSchema"] = schema
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
        """Convert Pydantic BaseModel or list[BaseModel] to Google JSON Schema format."""
        origin = get_origin(output_schema)
        if origin is list:
            inner_type = get_args(output_schema)[0]
            items_schema = inner_type.model_json_schema()
            # Extract $defs from items_schema and move to root (JSON Schema requires $defs at root)
            defs = items_schema.get("$defs", {})
            items_schema_clean = {k: v for k, v in items_schema.items() if k != "$defs"}
            json_schema = {"type": "array", "items": items_schema_clean}
            if defs:
                json_schema["$defs"] = defs
        else:
            json_schema = output_schema.model_json_schema()

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

    def _remove_unsupported_fields(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Remove unsupported metadata fields from schema."""
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
