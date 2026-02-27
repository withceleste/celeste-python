"""Constraint models for parameter validation."""

import math
import re
from abc import ABC, abstractmethod
from typing import Any, ClassVar, get_args, get_origin

from pydantic import BaseModel, Field, computed_field, field_serializer

from celeste.artifacts import AudioArtifact, ImageArtifact, VideoArtifact
from celeste.exceptions import ConstraintViolationError
from celeste.mime_types import AudioMimeType, ImageMimeType, MimeType, VideoMimeType
from celeste.tools import Tool


class Constraint(BaseModel, ABC):
    """Base constraint for parameter validation."""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def type(self) -> str:
        """Constraint type identifier for serialization."""
        return self.__class__.__name__

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
            raise ConstraintViolationError(msg)
        return value


class Range(Constraint):
    """Range constraint - value must be within min/max bounds.

    If step is provided, value must be at min + (n * step) for some integer n.
    If special_values is provided, those values bypass min/max validation.
    """

    min: float | int
    max: float | int
    step: float | None = None
    special_values: list[float | int] | None = None

    def __call__(self, value: float | int) -> float | int:
        """Validate value is within range and matches step increment."""
        if not isinstance(value, (int, float)):
            msg = f"Must be numeric, got {type(value).__name__}"
            raise ConstraintViolationError(msg)

        # Check if value is a special value that bypasses range check
        if self.special_values is not None and value in self.special_values:
            return value

        # Validate range
        if not self.min <= value <= self.max:
            special_msg = (
                f" or one of {self.special_values}" if self.special_values else ""
            )
            msg = (
                f"Must be between {self.min} and {self.max}{special_msg}, got {value!r}"
            )
            raise ConstraintViolationError(msg)

        # Validate step if provided
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
                msg = f"Value must match step {self.step}. Nearest valid: {closest_below} or {closest_above}, got {value!r}"
                raise ConstraintViolationError(msg)

        return value


class Pattern(Constraint):
    """Pattern constraint - value must match regex pattern."""

    pattern: str

    def __call__(self, value: str) -> str:
        """Validate value matches pattern."""
        if not isinstance(value, str):
            msg = f"Must be string, got {type(value).__name__}"
            raise ConstraintViolationError(msg)

        if not re.fullmatch(self.pattern, value):
            msg = f"Must match pattern {self.pattern!r}, got {value!r}"
            raise ConstraintViolationError(msg)

        return value


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


class Str(Constraint):
    """String type constraint with optional length validation."""

    max_length: int | None = None
    min_length: int | None = None

    def __call__(self, value: str) -> str:
        """Validate value is a string."""
        if not isinstance(value, str):
            msg = f"Must be string, got {type(value).__name__}"
            raise ConstraintViolationError(msg)

        if self.min_length is not None and len(value) < self.min_length:
            msg = f"String too short (min {self.min_length}), got length {len(value)}: {value!r}"
            raise ConstraintViolationError(msg)

        if self.max_length is not None and len(value) > self.max_length:
            msg = f"String too long (max {self.max_length}), got length {len(value)}: {value!r}"
            raise ConstraintViolationError(msg)

        return value


class Int(Constraint):
    """Integer type constraint."""

    def __call__(self, value: int | str | float) -> int:
        """Validate value is an integer or convert string/float to int."""
        if isinstance(value, str):
            if not value.lstrip("-").isdigit():
                msg = f"Must be int, got {value!r}"
                raise ConstraintViolationError(msg)
            return int(value)

        if isinstance(value, float):
            if not value.is_integer():
                msg = f"Must be int, got {value!r}"
                raise ConstraintViolationError(msg)
            return int(value)

        if not isinstance(value, int):
            msg = f"Must be int, got {type(value).__name__}"
            raise ConstraintViolationError(msg)

        return value


class Float(Constraint):
    """Float type constraint (accepts int as well)."""

    def __call__(self, value: float) -> float:
        """Validate value is numeric."""
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            msg = f"Must be float or int, got {type(value).__name__}"
            raise ConstraintViolationError(msg)

        return float(value)


class Bool(Constraint):
    """Boolean type constraint."""

    def __call__(self, value: bool) -> bool:
        """Validate value is a boolean."""
        if not isinstance(value, bool):
            msg = f"Must be bool, got {type(value).__name__}"
            raise ConstraintViolationError(msg)

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
                raise ConstraintViolationError(msg)
            return value

        # For plain type, validate directly
        if not (isinstance(value, type) and issubclass(value, BaseModel)):
            msg = f"Must be BaseModel, got {value}"
            raise ConstraintViolationError(msg)

        return value


class _MediaConstraint[M: MimeType](Constraint):
    """Base for single-media-artifact constraints."""

    _artifact_type: ClassVar[type]
    _media_label: ClassVar[str]

    supported_mime_types: list[M] | None = None

    def __call__(self, value: Any) -> Any:  # noqa: ANN401
        """Validate single media artifact against constraint."""
        if isinstance(value, list):
            msg = f"{self.__class__.__name__} requires a single {self._artifact_type.__name__}, not a list"
            raise ConstraintViolationError(msg)
        if not isinstance(value, self._artifact_type):
            msg = f"Must be {self._artifact_type.__name__}, got {type(value).__name__}"
            raise ConstraintViolationError(msg)
        if (
            self.supported_mime_types is not None
            and value.mime_type not in self.supported_mime_types  # type: ignore[attr-defined]
        ):
            supported_values = [mt.value for mt in self.supported_mime_types]
            got_value = value.mime_type.value if value.mime_type else None  # type: ignore[attr-defined]
            msg = f"mime_type must be one of {supported_values}, got {got_value!r}"
            raise ConstraintViolationError(msg)
        return value


class _MediaListConstraint[M: MimeType](Constraint):
    """Base for plural-media-artifact constraints."""

    _artifact_type: ClassVar[type]
    _media_label: ClassVar[str]

    supported_mime_types: list[M] | None = None
    max_count: int | None = None

    def __call__(self, value: Any) -> Any:  # noqa: ANN401
        """Validate media artifact(s) against constraint and normalize to list."""
        items = value if isinstance(value, list) else [value]
        if self.max_count is not None and len(items) > self.max_count:
            msg = f"Must have at most {self.max_count} {self._media_label}(s), got {len(items)}"
            raise ConstraintViolationError(msg)
        if self.supported_mime_types is not None:
            label = self._media_label.capitalize()
            for i, item in enumerate(items):
                if not isinstance(item, self._artifact_type):
                    msg = f"{label} {i + 1}: Must be {self._artifact_type.__name__}, got {type(item).__name__}"
                    raise ConstraintViolationError(msg)
                if item.mime_type not in self.supported_mime_types:  # type: ignore[attr-defined]
                    supported_values = [mt.value for mt in self.supported_mime_types]
                    got_value = item.mime_type.value if item.mime_type else None  # type: ignore[attr-defined]
                    msg = (
                        f"{label} {i + 1}: mime_type must be one of {supported_values}, "
                        f"got {got_value!r}"
                    )
                    raise ConstraintViolationError(msg)
        return items


class ImageConstraint(_MediaConstraint[ImageMimeType]):
    """Constraint for validating a single image artifact - validates mime_type."""

    _artifact_type = ImageArtifact
    _media_label = "image"


class ImagesConstraint(_MediaListConstraint[ImageMimeType]):
    """Constraint for validating image artifacts list - validates mime_type and count limits."""

    _artifact_type = ImageArtifact
    _media_label = "image"


class VideoConstraint(_MediaConstraint[VideoMimeType]):
    """Constraint for validating a single video artifact - validates mime_type."""

    _artifact_type = VideoArtifact
    _media_label = "video"


class VideosConstraint(_MediaListConstraint[VideoMimeType]):
    """Constraint for validating video artifacts list - validates mime_type and count limits."""

    _artifact_type = VideoArtifact
    _media_label = "video"


class AudioConstraint(_MediaConstraint[AudioMimeType]):
    """Constraint for validating a single audio artifact - validates mime_type."""

    _artifact_type = AudioArtifact
    _media_label = "audio"


class AudiosConstraint(_MediaListConstraint[AudioMimeType]):
    """Constraint for validating audio artifacts list - validates mime_type and count limits."""

    _artifact_type = AudioArtifact
    _media_label = "audio"


class ToolSupport(Constraint):
    """Tool support constraint - validates Tool instances are supported by the model."""

    tools: list[type[Tool]]

    @field_serializer("tools")
    @classmethod
    def _serialize_tools(cls, v: list[type[Tool]]) -> list[str]:
        return [t.__name__ for t in v]

    def __call__(self, value: list) -> list:
        """Validate tools list against supported tools."""
        for item in value:
            if isinstance(item, Tool) and type(item) not in self.tools:
                supported = [t.__name__ for t in self.tools]
                msg = f"Tool '{type(item).__name__}' not supported. Supported: {supported}"
                raise ConstraintViolationError(msg)
        return value


__all__ = [
    "AudioConstraint",
    "AudiosConstraint",
    "Bool",
    "Choice",
    "Constraint",
    "Dimensions",
    "Float",
    "ImageConstraint",
    "ImagesConstraint",
    "Int",
    "Pattern",
    "Range",
    "Schema",
    "Str",
    "ToolSupport",
    "VideoConstraint",
    "VideosConstraint",
]
