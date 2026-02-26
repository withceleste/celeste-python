"""OpenAI parameter mappers for text."""

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
from celeste.protocols.openresponses.parameters import (
    VerbosityMapper as _VerbosityMapper,
)
from celeste.types import TextContent

from ...parameters import TextParameter


class TemperatureMapper(_TemperatureMapper):
    """Map temperature to OpenAI's temperature parameter."""

    name = TextParameter.TEMPERATURE


class MaxTokensMapper(_MaxOutputTokensMapper):
    """Map max_tokens to OpenAI's max_output_tokens parameter."""

    name = TextParameter.MAX_TOKENS


class OutputSchemaMapper(_TextFormatMapper):
    """Map output_schema to OpenAI's text.format parameter."""

    name = TextParameter.OUTPUT_SCHEMA


class ToolsMapper(_ToolsMapper):
    """Map tools to OpenAI's tools parameter."""

    name = TextParameter.TOOLS


class VerbosityMapper(_VerbosityMapper):
    """Map verbosity to OpenAI's text.verbosity parameter."""

    name = TextParameter.VERBOSITY


class ThinkingBudgetMapper(_ReasoningEffortMapper):
    """Map thinking_budget to OpenAI's reasoning.effort parameter."""

    name = TextParameter.THINKING_BUDGET


OPENAI_PARAMETER_MAPPERS: list[ParameterMapper[TextContent]] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    OutputSchemaMapper(),
    ToolsMapper(),
    VerbosityMapper(),
    ThinkingBudgetMapper(),
]

__all__ = ["OPENAI_PARAMETER_MAPPERS"]
