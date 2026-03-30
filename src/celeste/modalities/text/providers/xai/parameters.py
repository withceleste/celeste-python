"""xAI parameter mappers for text."""

from celeste.parameters import ParameterMapper
from celeste.protocols.openresponses.parameters import (
    ReasoningEffortMapper as _ReasoningEffortMapper,
)
from celeste.types import TextContent

from ...parameters import TextParameter
from ...protocols.openresponses.parameters import OPENRESPONSES_PARAMETER_MAPPERS


class ThinkingBudgetMapper(_ReasoningEffortMapper):
    """Map thinking_budget to xAI's reasoning.effort parameter."""

    name = TextParameter.THINKING_BUDGET


XAI_PARAMETER_MAPPERS: list[ParameterMapper[TextContent]] = [
    *OPENRESPONSES_PARAMETER_MAPPERS,
    ThinkingBudgetMapper(),
]

__all__ = ["XAI_PARAMETER_MAPPERS"]
