"""XAI Responses parameter mappers for text generation."""

from celeste_xai.responses.parameters import (
    MaxTokensMapper as _MaxTokensMapper,
)
from celeste_xai.responses.parameters import (
    OutputSchemaMapper as _OutputSchemaMapper,
)
from celeste_xai.responses.parameters import (
    ReasoningEffortMapper as _ReasoningEffortMapper,
)
from celeste_xai.responses.parameters import (
    TemperatureMapper as _TemperatureMapper,
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


class OutputSchemaMapper(_OutputSchemaMapper):
    name = TextGenerationParameter.OUTPUT_SCHEMA


XAI_PARAMETER_MAPPERS: list[ParameterMapper] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    ThinkingBudgetMapper(),
    OutputSchemaMapper(),
]

__all__ = ["XAI_PARAMETER_MAPPERS"]
