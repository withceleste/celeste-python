"""Anthropic parameter mappers for text."""

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


class TemperatureMapper(_TemperatureMapper):
    """Map temperature to Anthropic's temperature parameter."""

    name = TextParameter.TEMPERATURE


class MaxTokensMapper(_MaxTokensMapper):
    """Map max_tokens to Anthropic's max_tokens parameter."""

    name = TextParameter.MAX_TOKENS


class ThinkingBudgetMapper(_ThinkingMapper):
    """Map thinking_budget to Anthropic's thinking parameter."""

    name = TextParameter.THINKING_BUDGET


class ThinkingLevelMapper(_ThinkingLevelMapper):
    """Map thinking_level to Anthropic's adaptive thinking + output_config.effort."""

    name = TextParameter.THINKING_LEVEL


class OutputSchemaMapper(_OutputFormatMapper):
    """Map output_schema to Anthropic's output_config.format parameter."""

    name = TextParameter.OUTPUT_SCHEMA


class ToolsMapper(_ToolsMapper):
    """Map tools to Anthropic's tools parameter."""

    name = TextParameter.TOOLS


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
