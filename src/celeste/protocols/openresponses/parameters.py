"""Responses API protocol parameter mappers."""

import json
from typing import Any, get_args, get_origin

from pydantic import BaseModel, TypeAdapter

from celeste.models import Model
from celeste.parameters import FieldMapper, ParameterMapper
from celeste.structured_outputs import StrictJsonSchemaGenerator
from celeste.tools import Tool
from celeste.types import TextContent

from .tools import TOOL_MAPPERS


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


class ToolsMapper(ParameterMapper[TextContent]):
    """Map tools list to Responses tools array."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform tools into provider request."""
        validated_value = self._validate_value(value, model)
        if not validated_value:
            return request

        dispatch = {m.tool_type: m for m in TOOL_MAPPERS}
        tools = request.setdefault("tools", [])

        for item in validated_value:
            if isinstance(item, Tool):
                mapper = dispatch.get(type(item))
                if mapper is None:
                    msg = f"Tool '{type(item).__name__}' is not supported by OpenResponses"
                    raise ValueError(msg)
                tools.append(mapper.map_tool(item))
            elif isinstance(item, dict) and "name" in item:
                tools.append(self._map_user_tool(item))
            elif isinstance(item, dict):
                tools.append(item)

        return request

    @staticmethod
    def _map_user_tool(tool: dict[str, Any]) -> dict[str, Any]:
        """Map a user-defined tool dict to OpenResponses wire format."""
        params = tool.get("parameters", {})
        if isinstance(params, type) and issubclass(params, BaseModel):
            schema = TypeAdapter(params).json_schema(
                schema_generator=StrictJsonSchemaGenerator,
                mode="serialization",
            )
        else:
            schema = params

        result: dict[str, Any] = {"type": "function", "name": tool["name"]}
        if "description" in tool:
            result["description"] = tool["description"]
        if schema:
            result["parameters"] = schema
        return result


__all__ = [
    "MaxOutputTokensMapper",
    "ReasoningEffortMapper",
    "TemperatureMapper",
    "TextFormatMapper",
    "ToolsMapper",
    "VerbosityMapper",
]
