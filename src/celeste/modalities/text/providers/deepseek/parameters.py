"""DeepSeek parameter mappers for text."""

from celeste.parameters import ParameterMapper
from celeste.providers.deepseek.chat.parameters import (
    ThinkingLevelMapper as _ThinkingLevelMapper,
)
from celeste.types import TextContent

from ...parameters import TextParameter
from ...protocols.chatcompletions.parameters import (
    MaxTokensMapper,
    OutputSchemaMapper,
    TemperatureMapper,
    ToolChoiceMapper,
    ToolsMapper,
)


class ThinkingLevelMapper(_ThinkingLevelMapper):
    """Map thinking_level to DeepSeek's thinking/reasoning_effort fields."""

    name = TextParameter.THINKING_LEVEL


DEEPSEEK_PARAMETER_MAPPERS: list[ParameterMapper[TextContent]] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    ThinkingLevelMapper(),
    OutputSchemaMapper(),
    ToolsMapper(),
    ToolChoiceMapper(),
]

__all__ = ["DEEPSEEK_PARAMETER_MAPPERS"]
