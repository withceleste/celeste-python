"""Google Interactions API parameter mappers."""

from typing import Any, ClassVar

from pydantic import BaseModel

from celeste.exceptions import InvalidToolError, ValidationError
from celeste.mime_types import AudioMimeType
from celeste.models import Model
from celeste.parameters import FieldMapper, ParameterMapper
from celeste.providers.google.generate_content.parameters import (
    ResponseJsonSchemaMapper,
)
from celeste.providers.google.utils import build_content_part
from celeste.tools import Tool, WebSearch
from celeste.types import (
    AudioContent,
    ImageContent,
    TextContent,
    VideoContent,
)

from .tools import TOOL_MAPPERS, WebSearchMapper

_TOOL_DISPATCH = {m.tool_type: m for m in TOOL_MAPPERS}


class TemperatureMapper(FieldMapper[TextContent]):
    """Map temperature to Google Interactions generation_config.temperature field."""

    field = "generation_config.temperature"


class MaxOutputTokensMapper(FieldMapper[TextContent]):
    """Map max_tokens to Google Interactions generation_config.max_output_tokens field."""

    field = "generation_config.max_output_tokens"


class SeedMapper(FieldMapper[TextContent]):
    """Map seed to Google Interactions generation_config.seed field."""

    field = "generation_config.seed"


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

        if isinstance(validated_value, Tool):
            msg = (
                f"Tool '{type(validated_value).__name__}' cannot be used "
                "as tool_choice in Google Interactions; select a function by name"
            )
            raise ValueError(msg)

        generation_config = request.setdefault("generation_config", {})
        if isinstance(validated_value, dict) and "name" in validated_value:
            generation_config["tool_choice"] = {
                "allowed_tools": {"mode": "any", "tools": [validated_value["name"]]}
            }
        elif validated_value == "required":
            generation_config["tool_choice"] = "any"
        elif (
            validated_value == "auto"
            and any(tool.get("type") == "function" for tool in request.get("tools", []))
            and any(tool.get("type") != "function" for tool in request.get("tools", []))
        ):
            generation_config["tool_choice"] = "validated"
        else:
            generation_config["tool_choice"] = str(validated_value).lower()
        return request


class ResponseFormatMapper(ResponseJsonSchemaMapper):
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


class AspectRatioMapper[Content](ParameterMapper[Content]):
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


class GoogleSearchMapper(ParameterMapper[ImageContent]):
    """Map grounding to a Google Interactions tools google_search entry."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Add the google_search tool when grounding is enabled."""
        validated_value = self._validate_value(value, model)
        if not validated_value:
            return request

        request.setdefault("tools", []).append(WebSearchMapper().map_tool(WebSearch()))
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


def _flat_input_parts(request: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize request input to a flat content-parts list (video task shape)."""
    current_input = request.get("input")
    if isinstance(current_input, str):
        parts: list[dict[str, Any]] = [{"type": "text", "text": current_input}]
    elif isinstance(current_input, list):
        parts = current_input
    else:
        parts = []
    request["input"] = parts
    return parts


def _set_video_task(request: dict[str, Any], task: str) -> None:
    """Set generation_config.video_config.task."""
    request.setdefault("generation_config", {}).setdefault("video_config", {})[
        "task"
    ] = task


class ResolutionMapper(ParameterMapper[VideoContent]):
    """Map resolution to Google Interactions response_format.resolution field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform resolution into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        response_format = request.setdefault("response_format", {"type": "video"})
        response_format["resolution"] = validated_value
        return request


class DurationMapper(ParameterMapper[VideoContent]):
    """Map duration to Google Interactions response_format.duration field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform duration into provider request."""
        if isinstance(value, str):
            value = int(value)

        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        response_format = request.setdefault("response_format", {"type": "video"})
        response_format["duration"] = f"{validated_value}s"
        return request


class FirstFrameMapper(ParameterMapper[VideoContent]):
    """Map first_frame to a leading image part with video_config.task image_to_video."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform first_frame into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        parts = _flat_input_parts(request)
        request["input"] = [build_content_part(validated_value, "image"), *parts]
        _set_video_task(request, "image_to_video")
        return request


class LastFrameMapper(ParameterMapper[VideoContent]):
    """Map last_frame to the second image part with video_config.task image_to_video."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform last_frame into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        parts = _flat_input_parts(request)
        if not parts or parts[0].get("type") != "image":
            msg = "last_frame requires first_frame to be provided"
            raise ValidationError(msg)
        request["input"] = [
            parts[0],
            build_content_part(validated_value, "image"),
            *parts[1:],
        ]
        _set_video_task(request, "image_to_video")
        return request


class ReferenceImagesMapper(ParameterMapper[VideoContent]):
    """Map reference_images to leading image parts with video_config.task reference_to_video."""

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

        parts = _flat_input_parts(request)
        image_parts = [build_content_part(img, "image") for img in validated_value]
        request["input"] = [*image_parts, *parts]
        _set_video_task(request, "reference_to_video")
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
    "DurationMapper",
    "FirstFrameMapper",
    "GoogleSearchMapper",
    "ImageSizeMapper",
    "LanguageMapper",
    "LastFrameMapper",
    "MaxOutputTokensMapper",
    "MediaContentMapper",
    "ReferenceImagesMapper",
    "ResolutionMapper",
    "ResponseFormatMapper",
    "SeedMapper",
    "TemperatureMapper",
    "ThinkingLevelMapper",
    "ToolChoiceMapper",
    "ToolsMapper",
    "VoiceMapper",
]
