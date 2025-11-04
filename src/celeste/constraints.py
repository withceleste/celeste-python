"""Constraint models for parameter validation."""

import math
import re
from abc import ABC, abstractmethod
from typing import Any, get_args, get_origin

from pydantic import BaseModel, Field


class Constraint(BaseModel, ABC):
    """Base constraint for parameter validation."""

    @abstractmethod
    def __call__(self, value: Any) -> Any:  # noqa: ANN401
        """Validate value against constraint and return validated value."""
        ...


class Choice[T](Constraint):
    """Choice constraint - value must be one of the provided options."""

    options: list[T] = Field(min_length=1)

    def __call__(self, value: T) -> T:
        """Validate value is in options."""
        if value not in self.options:
            msg = f"Must be one of {self.options}, got {value!r}"
            raise ValueError(msg)
        return value


class Range(Constraint):
    """Range constraint - value must be within min/max bounds.

    If step is provided, value must be at min + (n * step) for some integer n.
    """

    min: float | int
    max: float | int
    step: float | None = None

    def __call__(self, value: float | int) -> float | int:
        """Validate value is within range and matches step increment."""
        if not isinstance(value, (int, float)):
            msg = f"Must be numeric, got {type(value).__name__}"
            raise TypeError(msg)

        if not self.min <= value <= self.max:
            msg = f"Must be between {self.min} and {self.max}, got {value}"
            raise ValueError(msg)

        if self.step is not None:
            remainder = (value - self.min) % self.step
            # Use epsilon for floating-point comparison tolerance
            epsilon = 1e-9
            if not math.isclose(remainder, 0, abs_tol=epsilon) and not math.isclose(
                remainder, self.step, abs_tol=epsilon
            ):
                # Calculate nearest valid values for actionable error message
                closest_below = self.min + (
                    int((value - self.min) / self.step) * self.step
                )
                closest_above = closest_below + self.step
                msg = f"Value must match step {self.step}. Nearest valid: {closest_below} or {closest_above}, got {value}"
                raise ValueError(msg)

        return value


class Pattern(Constraint):
    """Pattern constraint - value must match regex pattern."""

    pattern: str

    def __call__(self, value: str) -> str:
        """Validate value matches pattern."""
        if not isinstance(value, str):
            msg = f"Must be string, got {type(value).__name__}"
            raise TypeError(msg)

        if not re.fullmatch(self.pattern, value):
            msg = f"Must match pattern {self.pattern!r}, got {value!r}"
            raise ValueError(msg)

        return value


class Str(Constraint):
    """String type constraint with optional length validation."""

    max_length: int | None = None
    min_length: int | None = None

    def __call__(self, value: str) -> str:
        """Validate value is a string."""
        if not isinstance(value, str):
            msg = f"Must be string, got {type(value).__name__}"
            raise TypeError(msg)

        if self.min_length is not None and len(value) < self.min_length:
            msg = f"String too short (min {self.min_length}), got {len(value)}"
            raise ValueError(msg)

        if self.max_length is not None and len(value) > self.max_length:
            msg = f"String too long (max {self.max_length}), got {len(value)}"
            raise ValueError(msg)

        return value


class Int(Constraint):
    """Integer type constraint."""

    def __call__(self, value: int) -> int:
        """Validate value is an integer."""
        # isinstance(True, int) is True, so exclude bools explicitly
        if not isinstance(value, int) or isinstance(value, bool):
            msg = f"Must be int, got {type(value).__name__}"
            raise TypeError(msg)

        return value


class Float(Constraint):
    """Float type constraint (accepts int as well)."""

    def __call__(self, value: float) -> float:
        """Validate value is numeric."""
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            msg = f"Must be float or int, got {type(value).__name__}"
            raise TypeError(msg)

        return float(value)


class Bool(Constraint):
    """Boolean type constraint."""

    def __call__(self, value: bool) -> bool:
        """Validate value is a boolean."""
        if not isinstance(value, bool):
            msg = f"Must be bool, got {type(value).__name__}"
            raise TypeError(msg)

        return value


class Schema(Constraint):
    """Schema constraint - value must be a Pydantic BaseModel subclass or list[BaseModel]."""

    def __call__(self, value: type[BaseModel]) -> type[BaseModel]:
        """Validate value is BaseModel or list[BaseModel]."""
        # For list[T], validate inner type T
        if get_origin(value) is list:
            inner = get_args(value)[0]
            if not (isinstance(inner, type) and issubclass(inner, BaseModel)):
                msg = f"List type must be BaseModel, got {inner}"
                raise TypeError(msg)
            return value

        # For plain type, validate directly
        if not (isinstance(value, type) and issubclass(value, BaseModel)):
            msg = f"Must be BaseModel, got {value}"
            raise TypeError(msg)

        return value


__all__ = [
    "Bool",
    "Choice",
    "Constraint",
    "Float",
    "Int",
    "Pattern",
    "Range",
    "Schema",
    "Str",
]
