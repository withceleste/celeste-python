"""Chat Completions protocol parameter mappers."""

import json
from typing import Any, ClassVar, get_origin

from pydantic import BaseModel, TypeAdapter

from celeste.exceptions import InvalidToolError
from celeste.models import Model
from celeste.parameters import FieldMapper, ParameterMapper
from celeste.structured_outputs import StrictJsonSchemaGenerator
from celeste.tools import Tool, ToolMapper
from celeste.types import TextContent

from .tools import TOOL_MAPPERS


class TemperatureMapper(FieldMapper[TextContent]):
    """Map temperature to Chat Completions temperature field."""

    field = "temperature"


class MaxTokensMapper(FieldMapper[TextContent]):
    """Map max_tokens to Chat Completions max_tokens field."""

    field = "max_tokens"


class ResponseFormatMapper(ParameterMapper[TextContent]):
    """Map output_schema to Chat Completions response_format field.

    Default uses json_object mode (no schema validation server-side).
    Providers with json_schema support override map() only.
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

        request["response_format"] = {"type": "json_object"}
        return request

    def parse_output(self, content: TextContent, value: object | None) -> TextContent:
        """Parse JSON string to typed output via Pydantic TypeAdapter."""
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
        if origin is list and isinstance(parsed, dict):
            if "items" in parsed:
                parsed = parsed["items"]
            else:
                parsed = list(parsed.values())

        return TypeAdapter(value).validate_python(parsed)


class ToolsMapper(ParameterMapper[TextContent]):
    """Map tools list to Chat Completions tools array.

    Subclasses override _tool_mappers with provider-specific built-in tool mappers.
    """

    _tool_mappers: ClassVar[list[ToolMapper]] = TOOL_MAPPERS

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

        dispatch = {m.tool_type: m for m in self._tool_mappers}
        tools = request.setdefault("tools", [])

        for item in validated_value:
            if isinstance(item, Tool):
                mapper = dispatch.get(type(item))
                if mapper is None:
                    msg = f"Tool '{type(item).__name__}' is not supported by this provider"
                    raise ValueError(msg)
                tools.append(mapper.map_tool(item))
            elif isinstance(item, dict) and "name" in item:
                tools.append(self._map_user_tool(item))
            elif isinstance(item, dict):
                tools.append(item)
            else:
                raise InvalidToolError(item)

        return request

    @staticmethod
    def _map_user_tool(tool: dict[str, Any]) -> dict[str, Any]:
        """Map a user-defined tool dict to Chat Completions function wire format."""
        params = tool.get("parameters", {})
        if isinstance(params, type) and issubclass(params, BaseModel):
            schema = TypeAdapter(params).json_schema(
                schema_generator=StrictJsonSchemaGenerator,
                mode="serialization",
            )
        else:
            schema = params

        function: dict[str, Any] = {"name": tool["name"]}
        if "description" in tool:
            function["description"] = tool["description"]
        if schema:
            function["parameters"] = schema

        return {"type": "function", "function": function}


__all__ = [
    "MaxTokensMapper",
    "ResponseFormatMapper",
    "TemperatureMapper",
    "ToolsMapper",
]
