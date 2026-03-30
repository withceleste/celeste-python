"""Moonshot parameter mappers for text."""

from celeste.parameters import ParameterMapper
from celeste.protocols.chatcompletions.parameters import (
    ToolsMapper as _ToolsMapper,
)
from celeste.providers.moonshot.chat.tools import TOOL_MAPPERS as MOONSHOT_TOOL_MAPPERS
from celeste.types import TextContent

from ...parameters import TextParameter
from ...protocols.chatcompletions.parameters import (
    MaxTokensMapper,
    OutputSchemaMapper,
    TemperatureMapper,
)


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
