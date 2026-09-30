"""OpenAI Live API parameter mappers."""

from typing import Any

from celeste.exceptions import InvalidToolError
from celeste.mime_types import AudioMimeType
from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.protocols.openresponses.parameters import ToolsMapper as _ToolsMapper
from celeste.protocols.openresponses.tools import TOOL_MAPPERS
from celeste.tools import Tool
from celeste.utils.mime import split_sample_rate

from .config import DEFAULT_AUDIO_FORMAT


class VoiceMapper[Content](ParameterMapper[Content]):
    """Map voice to OpenAI audio.output.voice field."""

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Transform voice into provider request."""
        value = self._validate_value(value, model)
        if value is not None:
            request.setdefault("audio", {}).setdefault("output", {})["voice"] = value
        return request


class AudioFormatMapper[Content](ParameterMapper[Content]):
    """Map audio_format to OpenAI audio.format field, shared by input and output."""

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Transform audio_format into provider request."""
        if isinstance(value, str):
            mime, rate = split_sample_rate(value)
            if rate is None:
                rate = (
                    8000
                    if mime in (AudioMimeType.PCMU, AudioMimeType.PCMA)
                    else DEFAULT_AUDIO_FORMAT["rate"]
                )
            value = {"type": mime, "rate": rate}
        value = self._validate_value(value, model)
        if value is not None:
            request.setdefault("audio", {})["format"] = value
        return request


class ToolsMapper[Content](ParameterMapper[Content]):
    """Map tools to OpenAI delegation.responses.tools field in Responses shape."""

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Transform tools into provider request."""
        validated = self._validate_value(value, model)
        if not validated:
            return request
        delegation = request.setdefault("delegation", {})
        delegation.setdefault("type", "responses")
        tools = delegation.setdefault("responses", {}).setdefault("tools", [])
        dispatch = {m.tool_type: m for m in TOOL_MAPPERS}
        for tool in validated:
            if isinstance(tool, Tool):
                mapper = dispatch.get(type(tool))
                if mapper is None:
                    raise ValueError(
                        f"OpenAI Live does not support {type(tool).__name__}"
                    )
                tools.append(mapper.map_tool(tool))
            elif isinstance(tool, dict) and "name" in tool:
                tools.append(_ToolsMapper._map_user_tool(tool))
            elif isinstance(tool, dict) and "type" in tool:
                tools.append(tool)
            else:
                raise InvalidToolError(tool)
        return request
