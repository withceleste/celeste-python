"""OpenRouter parameter mappers for text."""

from celeste.parameters import FieldMapper, ParameterMapper
from celeste.types import TextContent

from ...parameters import TextParameter
from ...protocols.openresponses.parameters import OPENRESPONSES_PARAMETER_MAPPERS


class PromptCacheKeyMapper(FieldMapper[TextContent]):
    """Map prompt_cache_key to OpenRouter's prompt_cache_key parameter."""

    name = TextParameter.PROMPT_CACHE_KEY
    field = "prompt_cache_key"


OPENROUTER_PARAMETER_MAPPERS: list[ParameterMapper[TextContent]] = [
    *OPENRESPONSES_PARAMETER_MAPPERS,
    PromptCacheKeyMapper(),
]

__all__ = ["OPENROUTER_PARAMETER_MAPPERS"]
