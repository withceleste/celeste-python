"""Parameter system for Celeste."""

from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any, TypedDict

from celeste.models import Model
from celeste.types import TextContent


class Parameters(TypedDict, total=False):
    """Base parameters for all capabilities."""


class ParameterMapper(ABC):
    """Base class for provider-specific parameter transformation."""

    name: StrEnum
    """Parameter name matching capability TypedDict key. Must be StrEnum for type safety."""

    @abstractmethod
    def map(self, request: dict[str, Any], value: Any, model: Model) -> dict[str, Any]:  # noqa: ANN401
        """Transform parameter value into provider's request structure.

        Args:
            request: Provider request dict.
            value: Parameter value.
            model: Model instance containing parameter_constraints for validation.

        Returns:
            Updated request dict.
        """
        ...

    def parse_output(self, content: TextContent, value: object | None) -> TextContent:
        """Optionally transform parsed content based on parameter value (default: return unchanged)."""
        return content

    def _validate_value(self, value: Any, model: Model) -> Any:  # noqa: ANN401
        """Validate parameter value using model constraint if present, otherwise pass through."""
        if value is None:
            return None

        constraint = model.parameter_constraints.get(self.name)
        if constraint is None:
            return value

        return constraint(value)


__all__ = ["ParameterMapper", "Parameters"]
