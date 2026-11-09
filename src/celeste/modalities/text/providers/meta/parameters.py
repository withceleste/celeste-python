"""Meta parameter mappers for text."""

from celeste.parameters import FieldMapper, ParameterMapper
from celeste.protocols.openresponses.parameters import (
    ReasoningEffortMapper as _ReasoningEffortMapper,
)
from celeste.types import TextContent

from ...parameters import TextParameter
from ...protocols.openresponses.parameters import OPENRESPONSES_PARAMETER_MAPPERS


class ThinkingLevelMapper(_ReasoningEffortMapper):
    """Map thinking_level to Meta's reasoning.effort parameter."""

    name = TextParameter.THINKING_LEVEL


class PromptCacheKeyMapper(FieldMapper[TextContent]):
    """Map prompt_cache_key to Meta's prompt_cache_key parameter."""

    name = TextParameter.PROMPT_CACHE_KEY
    field = "prompt_cache_key"


META_PARAMETER_MAPPERS: list[ParameterMapper[TextContent]] = [
    *OPENRESPONSES_PARAMETER_MAPPERS,
    ThinkingLevelMapper(),
    PromptCacheKeyMapper(),
]

__all__ = ["META_PARAMETER_MAPPERS"]
