"""OpenAI parameter mappers for text."""

from celeste.parameters import ParameterMapper
from celeste.providers.openai.responses.parameters import (
    MaxOutputTokensMapper as _MaxOutputTokensMapper,
)
from celeste.providers.openai.responses.parameters import (
    ReasoningEffortMapper as _ReasoningEffortMapper,
)
from celeste.providers.openai.responses.parameters import (
    TemperatureMapper as _TemperatureMapper,
)
from celeste.providers.openai.responses.parameters import (
    TextFormatMapper as _TextFormatMapper,
)
from celeste.providers.openai.responses.parameters import (
    VerbosityMapper as _VerbosityMapper,
)
from celeste.providers.openai.responses.parameters import (
    WebSearchMapper as _WebSearchMapper,
)

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


class WebSearchMapper(_WebSearchMapper):
    """Map web_search to OpenAI's tools parameter."""

    name = TextParameter.WEB_SEARCH


class VerbosityMapper(_VerbosityMapper):
    """Map verbosity to OpenAI's text.verbosity parameter."""

    name = TextParameter.VERBOSITY


class ThinkingBudgetMapper(_ReasoningEffortMapper):
    """Map thinking_budget to OpenAI's reasoning.effort parameter."""

    name = TextParameter.THINKING_BUDGET


OPENAI_PARAMETER_MAPPERS: list[ParameterMapper] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    OutputSchemaMapper(),
    WebSearchMapper(),
    VerbosityMapper(),
    ThinkingBudgetMapper(),
]

__all__ = ["OPENAI_PARAMETER_MAPPERS"]
