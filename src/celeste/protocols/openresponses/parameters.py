"""Responses API protocol parameter mappers."""

import json
from typing import Any, get_args, get_origin

from pydantic import BaseModel, TypeAdapter

from celeste.models import Model
from celeste.parameters import FieldMapper, ParameterMapper
from celeste.structured_outputs import StrictJsonSchemaGenerator
from celeste.types import TextContent


class TemperatureMapper(FieldMapper[TextContent]):
    """Map temperature to Responses temperature field."""

    field = "temperature"


class MaxOutputTokensMapper(FieldMapper[TextContent]):
    """Map max_tokens to Responses max_output_tokens field."""

    field = "max_output_tokens"


class TextFormatMapper(ParameterMapper[TextContent]):
    """Map output_schema to Responses text.format field.

    Handles both single BaseModel and list[BaseModel] types.
    Responses requires top-level object, so list types are wrapped.
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
            inner_type = get_args(validated_value)[0]
            inner_schema = TypeAdapter(inner_type).json_schema(
                schema_generator=StrictJsonSchemaGenerator,
                mode="serialization",
            )
            schema = {
                "type": "object",
                "properties": {"items": {"type": "array", "items": inner_schema}},
                "required": ["items"],
                "additionalProperties": False,
            }
            name = f"{inner_type.__name__.lower()}_list"
        else:
            schema = TypeAdapter(validated_value).json_schema(
                schema_generator=StrictJsonSchemaGenerator,
                mode="serialization",
            )
            name = validated_value.__name__.lower()

        request.setdefault("text", {})["format"] = {
            "type": "json_schema",
            "name": name,
            "schema": schema,
            "strict": True,
        }
        return request

    def parse_output(self, content: TextContent, value: object | None) -> TextContent:
        """Parse JSON string to BaseModel using Pydantic's TypeAdapter."""
        if value is None:
            return content

        if isinstance(content, BaseModel):
            return content
        if isinstance(content, list) and content and isinstance(content[0], BaseModel):
            return content

        if isinstance(content, str):
            parsed = json.loads(content, strict=False)
        else:
            parsed = content

        origin = get_origin(value)
        if origin is list and isinstance(parsed, dict) and "items" in parsed:
            parsed = parsed["items"]

        return TypeAdapter(value).validate_python(parsed)


class ReasoningEffortMapper(ParameterMapper[TextContent]):
    """Map reasoning_effort to Responses reasoning.effort field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform reasoning_effort into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request.setdefault("reasoning", {})["effort"] = validated_value
        return request


class VerbosityMapper(ParameterMapper[TextContent]):
    """Map verbosity to Responses text.verbosity field."""

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


class WebSearchMapper(ParameterMapper[TextContent]):
    """Map web_search to Responses tools array."""

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

        request.setdefault("tools", []).append({"type": "web_search"})
        return request


class XSearchMapper(ParameterMapper[TextContent]):
    """Map x_search to Responses tools array (search X/Twitter)."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform x_search into provider request."""
        validated_value = self._validate_value(value, model)
        if not validated_value:
            return request

        request.setdefault("tools", []).append({"type": "x_search"})
        return request


class CodeExecutionMapper(ParameterMapper[TextContent]):
    """Map code_execution to Responses tools array."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform code_execution into provider request."""
        validated_value = self._validate_value(value, model)
        if not validated_value:
            return request

        request.setdefault("tools", []).append({"type": "code_execution"})
        return request


__all__ = [
    "CodeExecutionMapper",
    "MaxOutputTokensMapper",
    "ReasoningEffortMapper",
    "TemperatureMapper",
    "TextFormatMapper",
    "VerbosityMapper",
    "WebSearchMapper",
    "XSearchMapper",
]
