"""Groq parameter mappers for text."""

from celeste.parameters import ParameterMapper
from celeste.protocols.chatcompletions.parameters import (
    ToolsMapper as _ToolsMapper,
)
from celeste.providers.groq.chat.parameters import (
    ResponseFormatMapper as _ResponseFormatMapper,
)
from celeste.providers.groq.chat.tools import TOOL_MAPPERS as GROQ_TOOL_MAPPERS
from celeste.types import TextContent

from ...parameters import TextParameter
from ...protocols.chatcompletions.parameters import (
    MaxTokensMapper,
    TemperatureMapper,
    ToolChoiceMapper,
)


class OutputSchemaMapper(_ResponseFormatMapper):
    """Map output_schema to Groq's response_format parameter."""

    name = TextParameter.OUTPUT_SCHEMA


class ToolsMapper(_ToolsMapper):
    """Map tools to Groq's tools parameter."""

    name = TextParameter.TOOLS
    _tool_mappers = GROQ_TOOL_MAPPERS


GROQ_PARAMETER_MAPPERS: list[ParameterMapper[TextContent]] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    OutputSchemaMapper(),
    ToolsMapper(),
    ToolChoiceMapper(),
]

__all__ = ["GROQ_PARAMETER_MAPPERS"]
