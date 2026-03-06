"""Moonshot parameter mappers for text."""

from celeste.parameters import ParameterMapper
from celeste.protocols.chatcompletions.parameters import (
    MaxTokensMapper as _MaxTokensMapper,
)
from celeste.protocols.chatcompletions.parameters import (
    ResponseFormatMapper as _ResponseFormatMapper,
)
from celeste.protocols.chatcompletions.parameters import (
    TemperatureMapper as _TemperatureMapper,
)
from celeste.protocols.chatcompletions.parameters import (
    ToolsMapper as _ToolsMapper,
)
from celeste.providers.moonshot.chat.tools import TOOL_MAPPERS as MOONSHOT_TOOL_MAPPERS
from celeste.types import TextContent

from ...parameters import TextParameter


class TemperatureMapper(_TemperatureMapper):
    """Map temperature to Moonshot's temperature parameter."""

    name = TextParameter.TEMPERATURE


class MaxTokensMapper(_MaxTokensMapper):
    """Map max_tokens to Moonshot's max_tokens parameter."""

    name = TextParameter.MAX_TOKENS


class OutputSchemaMapper(_ResponseFormatMapper):
    """Map output_schema to Moonshot's response_format parameter."""

    name = TextParameter.OUTPUT_SCHEMA


class ToolsMapper(_ToolsMapper):
    """Map tools to Moonshot's tools parameter."""

    name = TextParameter.TOOLS
    _tool_mappers = MOONSHOT_TOOL_MAPPERS


MOONSHOT_PARAMETER_MAPPERS: list[ParameterMapper[TextContent]] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    OutputSchemaMapper(),
    ToolsMapper(),
]

__all__ = ["MOONSHOT_PARAMETER_MAPPERS"]
