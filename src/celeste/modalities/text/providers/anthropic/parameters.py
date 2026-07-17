"""Anthropic parameter mappers for text."""

from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.providers.anthropic.messages.parameters import (
    MaxTokensMapper as _MaxTokensMapper,
)
from celeste.providers.anthropic.messages.parameters import (
    OutputFormatMapper as _OutputFormatMapper,
)
from celeste.providers.anthropic.messages.parameters import (
    TemperatureMapper as _TemperatureMapper,
)
from celeste.providers.anthropic.messages.parameters import (
    ThinkingLevelMapper as _ThinkingLevelMapper,
)
from celeste.providers.anthropic.messages.parameters import (
    ThinkingMapper as _ThinkingMapper,
)
from celeste.providers.anthropic.messages.parameters import (
    ToolChoiceMapper as _ToolChoiceMapper,
)
from celeste.providers.anthropic.messages.parameters import (
    ToolsMapper as _ToolsMapper,
)
from celeste.types import TextContent

from ...parameters import TextParameter
from .models import DYNAMIC_FILTERING_MODELS


class TemperatureMapper(_TemperatureMapper):
    """Map temperature to Anthropic's temperature parameter."""

    name = TextParameter.TEMPERATURE


class MaxTokensMapper(_MaxTokensMapper):
    """Map max_tokens to Anthropic's max_tokens parameter."""

    name = TextParameter.MAX_TOKENS


class ThinkingBudgetMapper(_ThinkingMapper):
    """Map thinking_budget to Anthropic's thinking parameter."""

    name = TextParameter.THINKING_BUDGET

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform thinking_budget with unified value translation."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        # Translate unified → provider-native
        if validated_value == -1:
            provider_value = "auto"
        else:
            provider_value = validated_value

        return super().map(request, provider_value, model)


class ThinkingLevelMapper(_ThinkingLevelMapper):
    """Map thinking_level to Anthropic's adaptive thinking + output_config.effort."""

    name = TextParameter.THINKING_LEVEL


class OutputSchemaMapper(_OutputFormatMapper):
    """Map output_schema to Anthropic's output_format parameter."""

    name = TextParameter.OUTPUT_SCHEMA


class ToolsMapper(_ToolsMapper):
    """Map tools to Anthropic's tools parameter (web_search version per model)."""

    name = TextParameter.TOOLS

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Upgrade web_search to dynamic filtering (web_search_20260209) where the model supports it."""
        request = super().map(request, value, model)
        if model.id in DYNAMIC_FILTERING_MODELS:
            for tool in request.get("tools", []):
                if tool.get("name") == "web_search":
                    tool["type"] = "web_search_20260209"
        return request


class ToolChoiceMapper(_ToolChoiceMapper):
    """Map tool_choice to Anthropic's tool_choice parameter."""

    name = TextParameter.TOOL_CHOICE


ANTHROPIC_PARAMETER_MAPPERS: list[ParameterMapper[TextContent]] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    ThinkingBudgetMapper(),
    ThinkingLevelMapper(),
    OutputSchemaMapper(),
    ToolsMapper(),
    ToolChoiceMapper(),
]

__all__ = ["ANTHROPIC_PARAMETER_MAPPERS"]
