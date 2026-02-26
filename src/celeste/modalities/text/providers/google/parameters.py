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
    ToolsMapper as _ToolsMapper,
)
from celeste.types import TextContent

from ...parameters import TextParameter


class TemperatureMapper(_TemperatureMapper[TextContent]):
    """Map temperature to Google's generationConfig.temperature parameter."""

    name = TextParameter.TEMPERATURE


class MaxTokensMapper(_MaxOutputTokensMapper[TextContent]):
    """Map max_tokens to Google's generationConfig.maxOutputTokens parameter."""

    name = TextParameter.MAX_TOKENS


class ThinkingBudgetMapper(_ThinkingBudgetMapper[TextContent]):
    """Map thinking_budget to Google's generationConfig.thinkingConfig.thinkingBudget parameter."""

    name = TextParameter.THINKING_BUDGET


class ThinkingLevelMapper(_ThinkingLevelMapper[TextContent]):
    """Map thinking_level to Google's generationConfig.thinkingConfig.thinkingLevel parameter."""

    name = TextParameter.THINKING_LEVEL


class OutputSchemaMapper(_ResponseJsonSchemaMapper):
    """Map output_schema to Google's generationConfig.responseJsonSchema parameter."""

    name = TextParameter.OUTPUT_SCHEMA


class ToolsMapper(_ToolsMapper[TextContent]):
    """Map tools to Google's tools parameter."""

    name = TextParameter.TOOLS


GOOGLE_PARAMETER_MAPPERS: list[ParameterMapper[TextContent]] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    ThinkingBudgetMapper(),
    ThinkingLevelMapper(),
    OutputSchemaMapper(),
    ToolsMapper(),
]

__all__ = ["GOOGLE_PARAMETER_MAPPERS"]
