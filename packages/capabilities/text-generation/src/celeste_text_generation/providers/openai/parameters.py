"""OpenAI Responses parameter mappers for text generation."""

from celeste_openai.responses.parameters import (
    MaxTokensMapper as _MaxTokensMapper,
)
from celeste_openai.responses.parameters import (
    OutputSchemaMapper as _OutputSchemaMapper,
)
from celeste_openai.responses.parameters import (
    ReasoningEffortMapper as _ReasoningEffortMapper,
)
from celeste_openai.responses.parameters import (
    TemperatureMapper as _TemperatureMapper,
)
from celeste_openai.responses.parameters import (
    VerbosityMapper as _VerbosityMapper,
)

from celeste.core import Parameter
from celeste.parameters import ParameterMapper
from celeste_text_generation.parameters import TextGenerationParameter


class TemperatureMapper(_TemperatureMapper):
    name = Parameter.TEMPERATURE


class MaxTokensMapper(_MaxTokensMapper):
    name = Parameter.MAX_TOKENS


class ThinkingBudgetMapper(_ReasoningEffortMapper):
    name = TextGenerationParameter.THINKING_BUDGET


class VerbosityMapper(_VerbosityMapper):
    name = TextGenerationParameter.VERBOSITY


class OutputSchemaMapper(_OutputSchemaMapper):
    name = TextGenerationParameter.OUTPUT_SCHEMA


OPENAI_PARAMETER_MAPPERS: list[ParameterMapper] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    ThinkingBudgetMapper(),
    VerbosityMapper(),
    OutputSchemaMapper(),
]

__all__ = ["OPENAI_PARAMETER_MAPPERS"]
