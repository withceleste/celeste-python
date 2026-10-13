"""OpenAI parameter mappers for text."""

from celeste.parameters import ParameterMapper
from celeste.protocols.openresponses.parameters import (
    ReasoningEffortMapper as _ReasoningEffortMapper,
)
from celeste.protocols.openresponses.parameters import (
    VerbosityMapper as _VerbosityMapper,
)
from celeste.types import TextContent

from ...parameters import TextParameter
from ...protocols.openresponses.parameters import OPENRESPONSES_PARAMETER_MAPPERS


class VerbosityMapper(_VerbosityMapper):
    """Map verbosity to OpenAI's text.verbosity parameter."""

    name = TextParameter.VERBOSITY


class ThinkingLevelMapper(_ReasoningEffortMapper):
    """Map thinking_level to OpenAI's reasoning.effort parameter."""

    name = TextParameter.THINKING_LEVEL


OPENAI_PARAMETER_MAPPERS: list[ParameterMapper[TextContent]] = [
    *OPENRESPONSES_PARAMETER_MAPPERS,
    VerbosityMapper(),
    ThinkingLevelMapper(),
]

__all__ = ["OPENAI_PARAMETER_MAPPERS"]
