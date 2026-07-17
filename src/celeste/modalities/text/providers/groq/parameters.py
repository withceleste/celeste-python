"""Groq parameter mappers for text."""

from celeste.parameters import ParameterMapper
from celeste.protocols.chatcompletions.parameters import (
    ToolsMapper as _ToolsMapper,
)
from celeste.providers.groq.chat.tools import TOOL_MAPPERS as GROQ_TOOL_MAPPERS
from celeste.types import TextContent

from ...parameters import TextParameter
from ...protocols.chatcompletions.parameters import (
    MaxTokensMapper,
    OutputSchemaMapper,
    TemperatureMapper,
    ThinkingBudgetMapper,
    ToolChoiceMapper,
)


class ToolsMapper(_ToolsMapper):
    """Map tools to Groq's tools parameter."""

    name = TextParameter.TOOLS
    _tool_mappers = GROQ_TOOL_MAPPERS


GROQ_PARAMETER_MAPPERS: list[ParameterMapper[TextContent]] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    ThinkingBudgetMapper(),
    OutputSchemaMapper(),
    ToolsMapper(),
    ToolChoiceMapper(),
]

__all__ = ["GROQ_PARAMETER_MAPPERS"]
