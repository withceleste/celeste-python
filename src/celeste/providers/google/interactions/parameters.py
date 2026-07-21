"""Google Interactions API parameter mappers."""

import json
from typing import Any, ClassVar, get_args, get_origin

from pydantic import BaseModel, TypeAdapter

from celeste.exceptions import InvalidToolError
from celeste.mime_types import AudioMimeType
from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.providers.google.utils import build_content_part
from celeste.tools import Tool
from celeste.types import AudioContent, ImageContent, TextContent

from .tools import TOOL_MAPPERS

_TOOL_DISPATCH = {m.tool_type: m for m in TOOL_MAPPERS}


class TemperatureMapper(ParameterMapper[TextContent]):
    """Map temperature to Google Interactions generation_config.temperature field."""

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

        request.setdefault("generation_config", {})["temperature"] = validated_value
        return request


class MaxOutputTokensMapper(ParameterMapper[TextContent]):
    """Map max_tokens to Google Interactions generation_config.max_output_tokens field."""

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

        request.setdefault("generation_config", {})["max_output_tokens"] = (
            validated_value
        )
        return request


class SeedMapper(ParameterMapper[TextContent]):
    """Map seed to Google Interactions generation_config.seed field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform seed into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request.setdefault("generation_config", {})["seed"] = validated_value
        return request


class ThinkingLevelMapper[Content](ParameterMapper[Content]):
    """Map thinking_level to Google Interactions generation_config.thinking_level field."""

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

        config = request.setdefault("generation_config", {})
        config["thinking_level"] = validated_value
        config["thinking_summaries"] = "auto"
        return request


class ToolsMapper(ParameterMapper[TextContent]):
    """Map tools list to Google Interactions tools field."""

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

        tools = request.setdefault("tools", [])

        for item in validated_value:
            if isinstance(item, Tool):
                mapper = _TOOL_DISPATCH.get(type(item))
                if mapper is None:
                    msg = f"Tool '{type(item).__name__}' is not supported by Google"
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
        """Map a user-defined tool dict to Google Interactions function tool format."""
        params = tool.get("parameters", {})
        if isinstance(params, type) and issubclass(params, BaseModel):
            schema = params.model_json_schema()
        else:
            schema = params

        result: dict[str, Any] = {"type": "function", "name": tool["name"]}
        if "description" in tool:
            result["description"] = tool["description"]
        if schema:
            result["parameters"] = schema
        return result


class ToolChoiceMapper(ParameterMapper[TextContent]):
    """Map tool_choice to Google Interactions generation_config.tool_choice field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform tool_choice into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        generation_config = request.setdefault("generation_config", {})

        if isinstance(validated_value, Tool):
            mapper = _TOOL_DISPATCH.get(type(validated_value))
            if mapper is None:
                msg = (
                    f"Tool '{type(validated_value).__name__}' cannot be used "
                    "as tool_choice in Google"
                )
                raise ValueError(msg)
            wire = mapper.map_tool(validated_value)
            generation_config["tool_choice"] = {
                "allowed_tools": {"mode": "any", "tools": [wire.get("name")]}
            }
        elif isinstance(validated_value, dict) and "name" in validated_value:
            generation_config["tool_choice"] = {
                "allowed_tools": {"mode": "any", "tools": [validated_value["name"]]}
            }
        elif validated_value == "required":
            generation_config["tool_choice"] = "any"
        else:
            generation_config["tool_choice"] = str(validated_value).lower()
        return request


class ResponseFormatMapper(ParameterMapper[TextContent]):
    """Map output_schema to Google Interactions response_format field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Add response_format (JSON schema) to request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        schema = self._convert_to_google_schema(validated_value)
        request["response_format"] = {
            "type": "text",
            "mime_type": "application/json",
            "schema": schema,
        }
        return request

    def parse_output(self, content: TextContent, value: object | None) -> TextContent:
        """Parse JSON to BaseModel using Pydantic's TypeAdapter."""
        if value is None:
            return content

        # If content is already a BaseModel, return it unchanged
        if isinstance(content, BaseModel):
            return content
        if isinstance(content, list) and content and isinstance(content[0], BaseModel):
            return content

        parsed = (
            json.loads(content, strict=False) if isinstance(content, str) else content
        )

        # For list[T], handle various formats Google might return
        origin = get_origin(value)
        if origin is list and isinstance(parsed, dict):
            # Google returns arrays directly in JSON schema, but might wrap in object
            if "items" in parsed:
                parsed = parsed["items"]
            else:
                # If it's a dict but not wrapped, try to extract array values
                parsed = list(parsed.values()) if parsed else []

        return TypeAdapter(value).validate_python(parsed)

    def _convert_to_google_schema(self, output_schema: Any) -> dict[str, Any]:  # noqa: ANN401
        """Convert Pydantic BaseModel or list[BaseModel] to Google JSON Schema format."""
        origin = get_origin(output_schema)
        if origin is list:
            inner_type = get_args(output_schema)[0]
            items_schema = inner_type.model_json_schema()
            defs = items_schema.get("$defs", {})
            items_schema_clean = {k: v for k, v in items_schema.items() if k != "$defs"}
            json_schema = {"type": "array", "items": items_schema_clean}
            if defs:
                json_schema["$defs"] = defs
        else:
            json_schema = output_schema.model_json_schema()

        json_schema = self._remove_unsupported_fields(json_schema)
        return json_schema

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


class AspectRatioMapper(ParameterMapper[ImageContent]):
    """Map aspect_ratio to Google Interactions response_format.aspect_ratio field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform aspect_ratio into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        response_format = request.setdefault("response_format", {"type": "image"})
        response_format["aspect_ratio"] = validated_value
        return request


class ImageSizeMapper(ParameterMapper[ImageContent]):
    """Map image_size to Google Interactions response_format.image_size field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform image_size into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        response_format = request.setdefault("response_format", {"type": "image"})
        response_format["image_size"] = validated_value
        return request


class MediaContentMapper[Content](ParameterMapper[Content]):
    """Map reference_images to Google Interactions input content."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform reference_images into provider request."""
        validated_value = self._validate_value(value, model)
        if not validated_value:
            return request

        image_parts = [build_content_part(img, "image") for img in validated_value]

        current_input = request.get("input")
        if (
            isinstance(current_input, list)
            and current_input
            and isinstance(current_input[0], dict)
            and isinstance(current_input[0].get("content"), list)
        ):
            current_input[0]["content"] = [
                *image_parts,
                *current_input[0]["content"],
            ]
        elif isinstance(current_input, list):
            request["input"] = [
                {"type": "user_input", "content": [*image_parts, *current_input]}
            ]
        elif isinstance(current_input, str):
            request["input"] = [
                {"type": "text", "text": current_input},
                *image_parts,
            ]
        else:
            request["input"] = [{"type": "user_input", "content": image_parts}]
        return request


class VoiceMapper(ParameterMapper[AudioContent]):
    """Map voice to Google Interactions generation_config.speech_config voice field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform voice into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        speech_config = request.setdefault("generation_config", {}).setdefault(
            "speech_config", [{}]
        )
        speech_config[0]["voice"] = validated_value
        return request


class LanguageMapper(ParameterMapper[AudioContent]):
    """Map language to Google Interactions generation_config.speech_config language field."""

    locale_map: ClassVar[dict[str, str]] = {}

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform language into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        locale = self.locale_map.get(str(validated_value), str(validated_value))
        speech_config = request.setdefault("generation_config", {}).setdefault(
            "speech_config", [{}]
        )
        speech_config[0]["language"] = locale
        return request


class AudioMimeTypeMapper(ParameterMapper[AudioContent]):
    """Map output_format to Google Interactions response_format.mime_type field."""

    mime_map: ClassVar[dict[AudioMimeType, str]] = {}

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform output_format into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        response_format = request.setdefault("response_format", {"type": "audio"})
        response_format["mime_type"] = self.mime_map[validated_value]
        return request


__all__ = [
    "AspectRatioMapper",
    "AudioMimeTypeMapper",
    "ImageSizeMapper",
    "LanguageMapper",
    "MaxOutputTokensMapper",
    "MediaContentMapper",
    "ResponseFormatMapper",
    "SeedMapper",
    "TemperatureMapper",
    "ThinkingLevelMapper",
    "ToolChoiceMapper",
    "ToolsMapper",
    "VoiceMapper",
]
