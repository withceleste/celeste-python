"""Meta parameter mappers for text."""

from celeste.parameters import ParameterMapper
from celeste.protocols.openresponses.parameters import (
    ReasoningEffortMapper as _ReasoningEffortMapper,
)
from celeste.types import TextContent

from ...parameters import TextParameter
from ...protocols.openresponses.parameters import OPENRESPONSES_PARAMETER_MAPPERS


class ThinkingLevelMapper(_ReasoningEffortMapper):
    """Map thinking_level to Meta's reasoning.effort parameter."""

    name = TextParameter.THINKING_LEVEL


META_PARAMETER_MAPPERS: list[ParameterMapper[TextContent]] = [
    *OPENRESPONSES_PARAMETER_MAPPERS,
    ThinkingLevelMapper(),
]

__all__ = ["META_PARAMETER_MAPPERS"]
