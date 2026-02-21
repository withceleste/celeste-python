"""Anthropic Messages API parameter mappers."""

import json
from typing import Any, get_args, get_origin

from pydantic import BaseModel, TypeAdapter

from celeste.models import Model
from celeste.parameters import FieldMapper, ParameterMapper
from celeste.structured_outputs import StrictJsonSchemaGenerator
from celeste.types import TextContent


class TemperatureMapper(FieldMapper):
    """Map temperature to Anthropic temperature field."""

    field = "temperature"


class TopPMapper(FieldMapper):
    """Map top_p to Anthropic top_p field."""

    field = "top_p"


class TopKMapper(FieldMapper):
    """Map top_k to Anthropic top_k field."""

    field = "top_k"


class MaxTokensMapper(FieldMapper):
    """Map max_tokens to Anthropic max_tokens field."""

    field = "max_tokens"


class StopSequencesMapper(FieldMapper):
    """Map stop_sequences to Anthropic stop_sequences field."""

    field = "stop_sequences"


class ThinkingMapper(ParameterMapper):
    """Map thinking to Anthropic thinking field.

    Accepts provider-native values:
    - "auto": Dynamic budget (API decides)
    - int: Fixed budget with specified tokens
    """

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform thinking into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        if validated_value == "auto":
            request["thinking"] = {"type": "auto"}
        else:
            request["thinking"] = {"type": "enabled", "budget_tokens": validated_value}
        return request


class WebSearchMapper(ParameterMapper):
    """Map web_search to Anthropic tools field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform web_search into provider request."""
        validated_value = self._validate_value(value, model)
        if not validated_value:
            return request

        request.setdefault("tools", []).append(
            {
                "type": "web_search_20250305",
                "name": "web_search",
            }
        )
        return request


class OutputFormatMapper(ParameterMapper):
    """Map output_schema to Anthropic output_format field.

    Handles both single BaseModel and list[BaseModel] types.
    Anthropic supports top-level arrays, $ref, and $defs natively.
    """

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

        origin = get_origin(validated_value)
        if origin is list:
            # Anthropic supports top-level arrays directly
            inner_type = get_args(validated_value)[0]
            inner_schema = TypeAdapter(inner_type).json_schema(
                schema_generator=StrictJsonSchemaGenerator,
                mode="serialization",
            )
            schema = {"type": "array", "items": inner_schema}
        else:
            schema = TypeAdapter(validated_value).json_schema(
                schema_generator=StrictJsonSchemaGenerator,
                mode="serialization",
            )

        request["output_format"] = {
            "type": "json_schema",
            "schema": schema,
        }

        # Signal that structured outputs beta header is needed
        request.setdefault("_beta_features", []).append("structured-outputs")

        return request

    def parse_output(self, content: TextContent, value: object | None) -> TextContent:
        """Parse JSON to BaseModel using Pydantic's TypeAdapter."""
        if value is None:
            return content if isinstance(content, str) else json.dumps(content)

        # If content is already a BaseModel, return it unchanged
        if isinstance(content, BaseModel):
            return content
        if isinstance(content, list) and content and isinstance(content[0], BaseModel):
            return content

        parsed: object
        if isinstance(content, dict):
            parsed = content
        elif isinstance(content, str):
            parsed = json.loads(content, strict=False)
        else:
            parsed = content

        return TypeAdapter(value).validate_python(parsed)


__all__ = [
    "MaxTokensMapper",
    "OutputFormatMapper",
    "StopSequencesMapper",
    "TemperatureMapper",
    "ThinkingMapper",
    "TopKMapper",
    "TopPMapper",
    "WebSearchMapper",
]
