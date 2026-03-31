"""Google GenerateContent API parameter mappers."""

import json
from typing import Any, get_args, get_origin

from pydantic import BaseModel, TypeAdapter

from celeste.exceptions import InvalidToolError
from celeste.mime_types import ApplicationMimeType
from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.providers.google.utils import build_media_part
from celeste.tools import Tool
from celeste.types import TextContent

from .tools import TOOL_MAPPERS


class TemperatureMapper[Content](ParameterMapper[Content]):
    """Map temperature to Google generationConfig.temperature field."""

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


class MaxOutputTokensMapper[Content](ParameterMapper[Content]):
    """Map max_tokens to Google generationConfig.maxOutputTokens field."""

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


class ThinkingBudgetMapper[Content](ParameterMapper[Content]):
    """Map thinkingBudget to Google generationConfig.thinkingConfig.thinkingBudget field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform thinkingBudget into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        thinking_config = request.setdefault("generationConfig", {}).setdefault(
            "thinkingConfig", {}
        )
        thinking_config["thinkingBudget"] = validated_value
        thinking_config.setdefault("includeThoughts", True)
        return request


class ThinkingLevelMapper[Content](ParameterMapper[Content]):
    """Map thinkingLevel to Google generationConfig.thinkingConfig.thinkingLevel field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform thinkingLevel into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        thinking_config = request.setdefault("generationConfig", {}).setdefault(
            "thinkingConfig", {}
        )
        thinking_config["thinkingLevel"] = validated_value
        thinking_config.setdefault("includeThoughts", True)
        return request


class AspectRatioMapper[Content](ParameterMapper[Content]):
    """Map aspect_ratio to Google generationConfig.imageConfig.aspectRatio field."""

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

        request.setdefault("generationConfig", {}).setdefault("imageConfig", {})[
            "aspectRatio"
        ] = validated_value
        return request


class ImageSizeMapper[Content](ParameterMapper[Content]):
    """Map image_size to Google generationConfig.imageConfig.imageSize field."""

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

        request.setdefault("generationConfig", {}).setdefault("imageConfig", {})[
            "imageSize"
        ] = validated_value
        return request


class MediaContentMapper[Content](ParameterMapper[Content]):
    """Map reference_images to Google contents.parts field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform reference_images into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        # Convert list of ImageArtifact to list of image parts
        image_parts = [build_media_part(img) for img in validated_value]

        # Add image parts before text in contents[0].parts
        if "contents" in request and len(request["contents"]) > 0:
            parts = request["contents"][0].get("parts", [])
            # Find text part and insert images before it
            text_index = next(
                (i for i, part in enumerate(parts) if "text" in part), len(parts)
            )
            # Insert image parts before text
            parts[text_index:text_index] = image_parts
            request["contents"][0]["parts"] = parts

        return request


class ToolsMapper[Content](ParameterMapper[Content]):
    """Map tools list to Google tools field."""

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
        fn_declarations: list[dict[str, Any]] = []

        for item in validated_value:
            if isinstance(item, Tool):
                mapper = dispatch.get(type(item))
                if mapper is None:
                    msg = f"Tool '{type(item).__name__}' is not supported by Google"
                    raise ValueError(msg)
                tools.append(mapper.map_tool(item))
            elif isinstance(item, dict) and "name" in item:
                fn_declarations.append(self._map_user_tool(item))
            elif isinstance(item, dict):
                tools.append(item)
            else:
                raise InvalidToolError(item)

        if fn_declarations:
            tools.append({"functionDeclarations": fn_declarations})

        return request

    @staticmethod
    def _map_user_tool(tool: dict[str, Any]) -> dict[str, Any]:
        """Map a user-defined tool dict to Google functionDeclaration format."""
        params = tool.get("parameters", {})
        if isinstance(params, type) and issubclass(params, BaseModel):
            schema = params.model_json_schema()
            # Remove unsupported 'title' fields
            schema = ToolsMapper._remove_titles(schema)
        else:
            schema = params

        result: dict[str, Any] = {"name": tool["name"]}
        if "description" in tool:
            result["description"] = tool["description"]
        if schema:
            result["parameters"] = schema
        return result

    @staticmethod
    def _remove_titles(schema: dict[str, Any]) -> dict[str, Any]:
        """Remove unsupported 'title' fields from schema for Google."""
        result: dict[str, Any] = {}
        for key, value in schema.items():
            if key == "title":
                continue
            if isinstance(value, dict):
                result[key] = ToolsMapper._remove_titles(value)
            elif isinstance(value, list):
                result[key] = [
                    ToolsMapper._remove_titles(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                result[key] = value
        return result


class ToolChoiceMapper[Content](ParameterMapper[Content]):
    """Map tool_choice to Google toolConfig.functionCallingConfig."""

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

        if isinstance(validated_value, Tool):
            dispatch = {m.tool_type: m for m in TOOL_MAPPERS}
            mapper = dispatch.get(type(validated_value))
            if mapper is None:
                msg = f"Tool '{type(validated_value).__name__}' cannot be used as tool_choice in Google"
                raise ValueError(msg)
            wire = mapper.map_tool(validated_value)
            config: dict[str, Any] = {
                "mode": "ANY",
                "allowedFunctionNames": [wire.get("name")],
            }
        elif isinstance(validated_value, dict) and "name" in validated_value:
            config = {
                "mode": "ANY",
                "allowedFunctionNames": [validated_value["name"]],
            }
        elif validated_value == "required":
            config = {"mode": "ANY"}
        else:
            config = {"mode": validated_value.upper()}
        request.setdefault("toolConfig", {})["functionCallingConfig"] = config
        return request


class ResponseJsonSchemaMapper(ParameterMapper[TextContent]):
    """Map output_schema to Google generationConfig.responseJsonSchema field."""

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

        schema = self._convert_to_google_schema(validated_value)

        config = request.setdefault("generationConfig", {})
        config["responseJsonSchema"] = schema
        config["responseMimeType"] = ApplicationMimeType.JSON

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


__all__ = [
    "AspectRatioMapper",
    "ImageSizeMapper",
    "MaxOutputTokensMapper",
    "MediaContentMapper",
    "ResponseJsonSchemaMapper",
    "TemperatureMapper",
    "ThinkingBudgetMapper",
    "ThinkingLevelMapper",
    "ToolChoiceMapper",
    "ToolsMapper",
]
