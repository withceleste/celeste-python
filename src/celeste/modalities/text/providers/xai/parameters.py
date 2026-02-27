"""xAI parameter mappers for text."""

from celeste.parameters import ParameterMapper
from celeste.protocols.openresponses.parameters import (
    MaxOutputTokensMapper as _MaxOutputTokensMapper,
)
from celeste.protocols.openresponses.parameters import (
    ReasoningEffortMapper as _ReasoningEffortMapper,
)
from celeste.protocols.openresponses.parameters import (
    TemperatureMapper as _TemperatureMapper,
)
from celeste.protocols.openresponses.parameters import (
    TextFormatMapper as _TextFormatMapper,
)
from celeste.protocols.openresponses.parameters import (
    ToolsMapper as _ToolsMapper,
)
from celeste.types import TextContent

from ...parameters import TextParameter


class TemperatureMapper(_TemperatureMapper):
    """Map temperature to xAI's temperature parameter."""

    name = TextParameter.TEMPERATURE


class MaxTokensMapper(_MaxOutputTokensMapper):
    """Map max_tokens to xAI's max_output_tokens parameter."""

    name = TextParameter.MAX_TOKENS


class ThinkingBudgetMapper(_ReasoningEffortMapper):
    """Map thinking_budget to xAI's reasoning.effort parameter."""

    name = TextParameter.THINKING_BUDGET


class OutputSchemaMapper(_TextFormatMapper):
    """Map output_schema to xAI's text.format parameter."""

    name = TextParameter.OUTPUT_SCHEMA


class ToolsMapper(_ToolsMapper):
    """Map tools to xAI's tools parameter."""

    name = TextParameter.TOOLS


XAI_PARAMETER_MAPPERS: list[ParameterMapper[TextContent]] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    ThinkingBudgetMapper(),
    OutputSchemaMapper(),
    ToolsMapper(),
]

__all__ = ["XAI_PARAMETER_MAPPERS"]
