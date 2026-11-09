"""xAI parameter mappers for text."""

from celeste.parameters import ParameterMapper
from celeste.protocols.openresponses.parameters import (
    ReasoningEffortMapper as _ReasoningEffortMapper,
)
from celeste.protocols.openresponses.parameters import (
    ToolsMapper as _ToolsMapper,
)
from celeste.providers.xai.responses.tools import TOOL_MAPPERS as XAI_TOOL_MAPPERS
from celeste.types import TextContent

from ...parameters import TextParameter
from ...protocols.openresponses.parameters import (
    MaxTokensMapper,
    OutputSchemaMapper,
    TemperatureMapper,
    ToolChoiceMapper,
)


class ThinkingLevelMapper(_ReasoningEffortMapper):
    """Map thinking_level to xAI's reasoning.effort parameter."""

    name = TextParameter.THINKING_LEVEL


class ToolsMapper(_ToolsMapper):
    """Map tools to xAI's tools parameter."""

    name = TextParameter.TOOLS
    _tool_mappers = XAI_TOOL_MAPPERS


XAI_PARAMETER_MAPPERS: list[ParameterMapper[TextContent]] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    OutputSchemaMapper(),
    ToolsMapper(),
    ToolChoiceMapper(),
    ThinkingLevelMapper(),
]

__all__ = ["XAI_PARAMETER_MAPPERS"]
