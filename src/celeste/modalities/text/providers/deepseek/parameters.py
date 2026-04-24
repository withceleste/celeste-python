"""DeepSeek parameter mappers for text."""

from celeste.parameters import ParameterMapper
from celeste.providers.deepseek.chat.parameters import (
    ThinkingLevelMapper as _ThinkingLevelMapper,
)
from celeste.types import TextContent

from ...parameters import TextParameter
from ...protocols.chatcompletions.parameters import CHATCOMPLETIONS_PARAMETER_MAPPERS


class ThinkingLevelMapper(_ThinkingLevelMapper):
    """Map thinking_level to DeepSeek's thinking/reasoning_effort fields."""

    name = TextParameter.THINKING_LEVEL


DEEPSEEK_PARAMETER_MAPPERS: list[ParameterMapper[TextContent]] = [
    *CHATCOMPLETIONS_PARAMETER_MAPPERS,
    ThinkingLevelMapper(),
]

__all__ = ["DEEPSEEK_PARAMETER_MAPPERS"]
