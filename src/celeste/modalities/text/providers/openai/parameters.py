"""OpenAI parameter mappers for text."""

from typing import Any

from celeste.parameters import ParameterMapper
from celeste.protocols.openresponses.parameters import (
    ReasoningEffortMapper as _ReasoningEffortMapper,
)
from celeste.protocols.openresponses.parameters import (
    ToolChoiceMapper as _ToolChoiceMapper,
)
from celeste.protocols.openresponses.parameters import (
    VerbosityMapper as _VerbosityMapper,
)
from celeste.tools import Tool, WebSearch
from celeste.types import TextContent

from ...parameters import TextParameter
from ...protocols.openresponses.parameters import OPENRESPONSES_PARAMETER_MAPPERS


class VerbosityMapper(_VerbosityMapper):
    """Map verbosity to OpenAI's text.verbosity parameter."""

    name = TextParameter.VERBOSITY


class ThinkingLevelMapper(_ReasoningEffortMapper):
    """Map thinking_level to OpenAI's reasoning.effort parameter."""

    name = TextParameter.THINKING_LEVEL


class ToolChoiceMapper(_ToolChoiceMapper):
    """Select OpenAI web search using the Responses allowed-tools selector."""

    name = TextParameter.TOOL_CHOICE

    def _map_tool_choice(self, tool: Tool) -> dict[str, Any]:
        """Select native web search or delegate supported function choices."""
        if isinstance(tool, WebSearch):
            return {
                "type": "allowed_tools",
                "mode": "required",
                "tools": [{"type": "web_search"}],
            }
        return super()._map_tool_choice(tool)


OPENAI_PARAMETER_MAPPERS: list[ParameterMapper[TextContent]] = [
    *[
        mapper
        for mapper in OPENRESPONSES_PARAMETER_MAPPERS
        if mapper.name != TextParameter.TOOL_CHOICE
    ],
    ToolChoiceMapper(),
    VerbosityMapper(),
    ThinkingLevelMapper(),
]

__all__ = ["OPENAI_PARAMETER_MAPPERS"]
