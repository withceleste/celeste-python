"""Moonshot parameter mappers for text."""

from celeste.parameters import ParameterMapper
from celeste.protocols.chatcompletions.parameters import (
    ToolsMapper as _ToolsMapper,
)
from celeste.providers.moonshot.chat.tools import TOOL_MAPPERS as MOONSHOT_TOOL_MAPPERS
from celeste.types import TextContent

from ...parameters import TextParameter
from ...protocols.chatcompletions.parameters import (
    MaxTokensMapper as _MaxTokensMapper,
)
from ...protocols.chatcompletions.parameters import (
    OutputSchemaMapper,
    TemperatureMapper,
    ThinkingBudgetMapper,
)
from ...protocols.chatcompletions.parameters import (
    ToolChoiceMapper as _ToolChoiceMapper,
)


class ToolsMapper(_ToolsMapper):
    """Map tools to Moonshot's tools parameter."""

    name = TextParameter.TOOLS
    _tool_mappers = MOONSHOT_TOOL_MAPPERS


class ToolChoiceMapper(_ToolChoiceMapper):
    name = TextParameter.TOOL_CHOICE


class MaxTokensMapper(_MaxTokensMapper):
    """Map max_tokens to Moonshot's current field name."""

    field = "max_completion_tokens"


MOONSHOT_PARAMETER_MAPPERS: list[ParameterMapper[TextContent]] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    ThinkingBudgetMapper(),
    OutputSchemaMapper(),
    ToolsMapper(),
    ToolChoiceMapper(),
]

__all__ = ["MOONSHOT_PARAMETER_MAPPERS"]
