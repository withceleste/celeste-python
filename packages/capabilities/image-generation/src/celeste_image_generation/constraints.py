"""Image generation specific constraints."""

from celeste.constraints import Constraint
from celeste.exceptions import ConstraintViolationError


class Dimensions(Constraint):
    """Dimension string constraint with pixel and aspect ratio bounds."""

    min_pixels: int
    max_pixels: int
    min_aspect_ratio: float
    max_aspect_ratio: float
    presets: dict[str, str] | None = None

    def __call__(self, value: str) -> str:
        """Validate dimension string against pixel and aspect ratio bounds."""
        if not isinstance(value, str):
            msg = f"Must be string, got {type(value).__name__}"
            raise ConstraintViolationError(msg)

        # Check if value is a preset key
        if self.presets and value in self.presets:
            actual_value = self.presets[value]
        else:
            actual_value = value

        # Parse dimension format "WIDTHxHEIGHT"
        parts = actual_value.lower().split("x")
        if len(parts) != 2:
            msg = f"Invalid dimension format: {actual_value!r}. Expected 'WIDTHxHEIGHT'"
            raise ConstraintViolationError(msg)

        # Validate parts are numeric
        if not parts[0].isdigit() or not parts[1].isdigit():
            msg = (
                f"Invalid dimension format: {actual_value!r}. "
                f"Width and height must be positive integers"
            )
            raise ConstraintViolationError(msg)

        width = int(parts[0])
        height = int(parts[1])

        # Validate dimensions are positive
        if width <= 0 or height <= 0:
            msg = f"Width and height must be positive, got {width}x{height}"
            raise ConstraintViolationError(msg)

        # Validate total pixels
        total_pixels = width * height
        if not (self.min_pixels <= total_pixels <= self.max_pixels):
            msg = (
                f"Total pixels {total_pixels:,} outside valid range "
                f"[{self.min_pixels:,}, {self.max_pixels:,}]"
            )
            raise ConstraintViolationError(msg)

        # Validate aspect ratio
        aspect_ratio = width / height
        if not (self.min_aspect_ratio <= aspect_ratio <= self.max_aspect_ratio):
            msg = (
                f"Aspect ratio {aspect_ratio:.3f} outside valid range "
                f"[{self.min_aspect_ratio:.3f}, {self.max_aspect_ratio:.3f}]"
            )
            raise ConstraintViolationError(msg)

        # Return normalized format
        return f"{width}x{height}"


__all__ = ["Dimensions"]
