"""Google Live API parameter mappers."""

from typing import Any

from celeste.exceptions import InvalidToolError
from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.providers.google.generate_content.parameters import (
    MaxOutputTokensMapper,
    SeedMapper,
    TemperatureMapper,
)
from celeste.providers.google.generate_content.parameters import (
    ToolsMapper as _ToolsMapper,
)
from celeste.providers.google.generate_content.tools import WebSearchMapper
from celeste.providers.google.utils import build_media_part
from celeste.tools import Tool, WebSearch


class VoiceNameMapper[Content](ParameterMapper[Content]):
    """Map voice to Google generationConfig.speechConfig voiceName field."""

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Transform voice into provider request."""
        value = self._validate_value(value, model)
        if value is not None:
            request.setdefault("generationConfig", {}).setdefault(
                "speechConfig", {}
            ).setdefault("voiceConfig", {})["prebuiltVoiceConfig"] = {
                "voiceName": value
            }
        return request


class MediaContentMapper[Content](ParameterMapper[Content]):
    """Map reference images to Google clientContent.turns field."""

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Transform reference images into provider request."""
        validated = self._validate_value(value, model)
        if validated:
            request.setdefault("clientContent", {"turnComplete": False}).setdefault(
                "turns", []
            ).append(
                {"role": "user", "parts": [build_media_part(img) for img in validated]}
            )
        return request


class ThinkingLevelMapper[Content](ParameterMapper[Content]):
    """Map thinking_level to Google generationConfig.thinkingConfig.thinkingLevel field."""

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Transform thinking_level into provider request."""
        value = self._validate_value(value, model)
        if value is not None:
            request.setdefault("generationConfig", {}).setdefault("thinkingConfig", {})[
                "thinkingLevel"
            ] = value
        return request


class ToolsMapper[Content](ParameterMapper[Content]):
    """Map tools to Google tools field with non-blocking function declarations."""

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Transform tools into provider request."""
        validated = self._validate_value(value, model)
        if not validated:
            return request
        tools = request.setdefault("tools", [])
        functions = []
        for tool in validated:
            if isinstance(tool, WebSearch):
                tools.append(WebSearchMapper().map_tool(tool))
            elif isinstance(tool, Tool):
                raise ValueError(f"Google Live does not support {type(tool).__name__}")
            elif isinstance(tool, dict) and "name" in tool:
                functions.append(
                    {**_ToolsMapper._map_user_tool(tool), "behavior": "NON_BLOCKING"}
                )
            elif isinstance(tool, dict):
                tools.append(tool)
            else:
                raise InvalidToolError(tool)
        if functions:
            tools.append({"functionDeclarations": functions})
        return request


__all__ = [
    "MaxOutputTokensMapper",
    "MediaContentMapper",
    "SeedMapper",
    "TemperatureMapper",
    "ThinkingLevelMapper",
    "ToolsMapper",
    "VoiceNameMapper",
]
