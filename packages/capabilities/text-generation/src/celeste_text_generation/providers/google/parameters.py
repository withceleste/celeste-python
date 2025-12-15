"""Google Gemini parameter mappers for text generation."""

from celeste_google.generate_content.parameters import (
    MaxOutputTokensMapper as _MaxOutputTokensMapper,
)
from celeste_google.generate_content.parameters import (
    OutputSchemaMapper as _OutputSchemaMapper,
)
from celeste_google.generate_content.parameters import (
    TemperatureMapper as _TemperatureMapper,
)
from celeste_google.generate_content.parameters import (
    ThinkingBudgetMapper as _ThinkingBudgetMapper,
)
from celeste_google.generate_content.parameters import (
    ThinkingLevelMapper as _ThinkingLevelMapper,
)

from celeste.core import Parameter
from celeste.parameters import ParameterMapper
from celeste_text_generation.parameters import TextGenerationParameter


class TemperatureMapper(_TemperatureMapper):
    name = Parameter.TEMPERATURE


class MaxTokensMapper(_MaxOutputTokensMapper):
    name = Parameter.MAX_TOKENS


class ThinkingBudgetMapper(_ThinkingBudgetMapper):
    name = TextGenerationParameter.THINKING_BUDGET


class ThinkingLevelMapper(_ThinkingLevelMapper):
    name = TextGenerationParameter.THINKING_LEVEL


class OutputSchemaMapper(_OutputSchemaMapper):
    name = TextGenerationParameter.OUTPUT_SCHEMA


GOOGLE_PARAMETER_MAPPERS: list[ParameterMapper] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    ThinkingBudgetMapper(),
    ThinkingLevelMapper(),
    OutputSchemaMapper(),
]

__all__ = ["GOOGLE_PARAMETER_MAPPERS"]
