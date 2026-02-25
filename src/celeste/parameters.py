"""Parameter system for Celeste."""

from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any, ClassVar, TypedDict

from celeste.models import Model


class Parameters(TypedDict, total=False):
    """Base parameters for all capabilities."""


class ParameterMapper[Content](ABC):
    """Base class for provider-specific parameter transformation."""

    name: ClassVar[StrEnum]
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

    def parse_output(self, content: Content, value: object | None) -> Content:
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


class FieldMapper[Content](ParameterMapper[Content]):
    """Maps a parameter directly to a flat request field after validation."""

    field: ClassVar[str]

    def map(self, request: dict[str, Any], value: Any, model: Model) -> dict[str, Any]:  # noqa: ANN401
        """Transform parameter value into provider's request structure."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request
        request[self.field] = validated_value
        return request


__all__ = ["FieldMapper", "ParameterMapper", "Parameters"]
