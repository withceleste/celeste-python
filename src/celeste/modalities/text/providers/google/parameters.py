"""Google parameter mappers for text."""

from celeste.parameters import ParameterMapper
from celeste.providers.google.generate_content.parameters import (
    MaxOutputTokensMapper as _MaxOutputTokensMapper,
)
from celeste.providers.google.generate_content.parameters import (
    ResponseJsonSchemaMapper as _ResponseJsonSchemaMapper,
)
from celeste.providers.google.generate_content.parameters import (
    TemperatureMapper as _TemperatureMapper,
)
from celeste.providers.google.generate_content.parameters import (
    ThinkingBudgetMapper as _ThinkingBudgetMapper,
)
from celeste.providers.google.generate_content.parameters import (
    ThinkingLevelMapper as _ThinkingLevelMapper,
)
from celeste.providers.google.generate_content.parameters import (
    WebSearchMapper as _WebSearchMapper,
)

from ...parameters import TextParameter


class TemperatureMapper(_TemperatureMapper):
    """Map temperature to Google's generationConfig.temperature parameter."""

    name = TextParameter.TEMPERATURE


class MaxTokensMapper(_MaxOutputTokensMapper):
    """Map max_tokens to Google's generationConfig.maxOutputTokens parameter."""

    name = TextParameter.MAX_TOKENS


class ThinkingBudgetMapper(_ThinkingBudgetMapper):
    """Map thinking_budget to Google's generationConfig.thinkingConfig.thinkingBudget parameter."""

    name = TextParameter.THINKING_BUDGET


class ThinkingLevelMapper(_ThinkingLevelMapper):
    """Map thinking_level to Google's generationConfig.thinkingConfig.thinkingLevel parameter."""

    name = TextParameter.THINKING_LEVEL


class OutputSchemaMapper(_ResponseJsonSchemaMapper):
    """Map output_schema to Google's generationConfig.responseJsonSchema parameter."""

    name = TextParameter.OUTPUT_SCHEMA


class WebSearchMapper(_WebSearchMapper):
    """Map web_search to Google's tools parameter."""

    name = TextParameter.WEB_SEARCH


GOOGLE_PARAMETER_MAPPERS: list[ParameterMapper] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    ThinkingBudgetMapper(),
    ThinkingLevelMapper(),
    OutputSchemaMapper(),
    WebSearchMapper(),
]

__all__ = ["GOOGLE_PARAMETER_MAPPERS"]
