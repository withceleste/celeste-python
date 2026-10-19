"""OpenAI parameter mappers for text."""

from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.protocols.openresponses.parameters import (
    ReasoningEffortMapper as _ReasoningEffortMapper,
)
from celeste.protocols.openresponses.parameters import (
    VerbosityMapper as _VerbosityMapper,
)
from celeste.tools import WebSearch
from celeste.types import TextContent

from ...parameters import TextParameter
from ...protocols.openresponses.parameters import (
    MaxTokensMapper,
    OutputSchemaMapper,
    TemperatureMapper,
    ToolsMapper,
)
from ...protocols.openresponses.parameters import (
    ToolChoiceMapper as _ToolChoiceMapper,
)


class VerbosityMapper(_VerbosityMapper):
    """Map verbosity to OpenAI's text.verbosity parameter."""

    name = TextParameter.VERBOSITY


class ThinkingLevelMapper(_ReasoningEffortMapper):
    """Map thinking_level to OpenAI's reasoning.effort parameter."""

    name = TextParameter.THINKING_LEVEL


class ToolChoiceMapper(_ToolChoiceMapper):
    """Select OpenAI web search using the Responses allowed-tools selector."""

    name = TextParameter.TOOL_CHOICE

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform tool_choice, selecting WebSearch via allowed_tools."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request
        if isinstance(validated_value, WebSearch):
            request["tool_choice"] = {
                "type": "allowed_tools",
                "mode": "required",
                "tools": [{"type": "web_search"}],
            }
            return request
        return super().map(request, validated_value, model)


OPENAI_PARAMETER_MAPPERS: list[ParameterMapper[TextContent]] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    OutputSchemaMapper(),
    ToolsMapper(),
    ToolChoiceMapper(),
    VerbosityMapper(),
    ThinkingLevelMapper(),
]

__all__ = ["OPENAI_PARAMETER_MAPPERS"]
