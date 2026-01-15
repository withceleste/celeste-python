"""Constraint models for parameter validation."""

import math
import re
from abc import ABC, abstractmethod
from typing import Any, get_args, get_origin

from pydantic import BaseModel, Field, computed_field

from celeste.artifacts import AudioArtifact, ImageArtifact, VideoArtifact
from celeste.exceptions import ConstraintViolationError
from celeste.mime_types import AudioMimeType, ImageMimeType, VideoMimeType
from celeste.types import AudioContent, ImageContent, VideoContent


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


class ImageConstraint(Constraint):
    """Constraint for validating a single image artifact - validates mime_type."""

    supported_mime_types: list[ImageMimeType] | None = None
    """Supported MIME types for the image."""

    def __call__(self, value: ImageArtifact) -> ImageArtifact:
        """Validate single image artifact against constraint."""
        if isinstance(value, list):
            msg = "ImageConstraint requires a single ImageArtifact, not a list"
            raise ConstraintViolationError(msg)

        if not isinstance(value, ImageArtifact):
            msg = f"Must be ImageArtifact, got {type(value).__name__}"
            raise ConstraintViolationError(msg)

        if (
            self.supported_mime_types is not None
            and value.mime_type not in self.supported_mime_types
        ):
            supported_values = [mt.value for mt in self.supported_mime_types]
            got_value = value.mime_type.value if value.mime_type else None
            msg = f"mime_type must be one of {supported_values}, got {got_value!r}"
            raise ConstraintViolationError(msg)

        return value


class ImagesConstraint(Constraint):
    """Constraint for validating image artifacts list - validates mime_type and count limits."""

    supported_mime_types: list[ImageMimeType] | None = None
    """Supported MIME types."""

    max_count: int | None = None
    """Maximum number of images."""

    def __call__(self, value: ImageContent) -> list[ImageArtifact]:
        """Validate image artifact(s) against constraint and normalize to list."""
        # Normalize: if single ImageArtifact is passed, wrap it in a list
        images = value if isinstance(value, list) else [value]

        if self.max_count is not None and len(images) > self.max_count:
            msg = f"Must have at most {self.max_count} image(s), got {len(images)}"
            raise ConstraintViolationError(msg)

        if self.supported_mime_types is not None:
            for i, img in enumerate(images):
                if not isinstance(img, ImageArtifact):
                    msg = f"Image {i + 1}: Must be ImageArtifact, got {type(img).__name__}"
                    raise ConstraintViolationError(msg)
                if img.mime_type not in self.supported_mime_types:
                    supported_values = [mt.value for mt in self.supported_mime_types]
                    got_value = img.mime_type.value if img.mime_type else None
                    msg = (
                        f"Image {i + 1}: mime_type must be one of {supported_values}, "
                        f"got {got_value!r}"
                    )
                    raise ConstraintViolationError(msg)

        return images


class VideoConstraint(Constraint):
    """Constraint for validating a single video artifact - validates mime_type."""

    supported_mime_types: list[VideoMimeType] | None = None
    """Supported MIME types for the video."""

    def __call__(self, value: VideoArtifact) -> VideoArtifact:
        """Validate single video artifact against constraint."""
        if isinstance(value, list):
            msg = "VideoConstraint requires a single VideoArtifact, not a list"
            raise ConstraintViolationError(msg)

        if not isinstance(value, VideoArtifact):
            msg = f"Must be VideoArtifact, got {type(value).__name__}"
            raise ConstraintViolationError(msg)

        if (
            self.supported_mime_types is not None
            and value.mime_type not in self.supported_mime_types
        ):
            supported_values = [mt.value for mt in self.supported_mime_types]
            got_value = value.mime_type.value if value.mime_type else None
            msg = f"mime_type must be one of {supported_values}, got {got_value!r}"
            raise ConstraintViolationError(msg)

        return value


class VideosConstraint(Constraint):
    """Constraint for validating video artifacts list - validates mime_type and count limits."""

    supported_mime_types: list[VideoMimeType] | None = None
    """Supported MIME types."""

    max_count: int | None = None
    """Maximum number of videos."""

    def __call__(self, value: VideoContent) -> list[VideoArtifact]:
        """Validate video artifact(s) against constraint and normalize to list."""
        # Normalize: if single VideoArtifact is passed, wrap it in a list
        videos = value if isinstance(value, list) else [value]

        if self.max_count is not None and len(videos) > self.max_count:
            msg = f"Must have at most {self.max_count} video(s), got {len(videos)}"
            raise ConstraintViolationError(msg)

        if self.supported_mime_types is not None:
            for i, vid in enumerate(videos):
                if not isinstance(vid, VideoArtifact):
                    msg = f"Video {i + 1}: Must be VideoArtifact, got {type(vid).__name__}"
                    raise ConstraintViolationError(msg)
                if vid.mime_type not in self.supported_mime_types:
                    supported_values = [mt.value for mt in self.supported_mime_types]
                    got_value = vid.mime_type.value if vid.mime_type else None
                    msg = (
                        f"Video {i + 1}: mime_type must be one of {supported_values}, "
                        f"got {got_value!r}"
                    )
                    raise ConstraintViolationError(msg)

        return videos


class AudioConstraint(Constraint):
    """Constraint for validating a single audio artifact - validates mime_type."""

    supported_mime_types: list[AudioMimeType] | None = None
    """Supported MIME types for the audio."""

    def __call__(self, value: AudioArtifact) -> AudioArtifact:
        """Validate single audio artifact against constraint."""
        if isinstance(value, list):
            msg = "AudioConstraint requires a single AudioArtifact, not a list"
            raise ConstraintViolationError(msg)

        if not isinstance(value, AudioArtifact):
            msg = f"Must be AudioArtifact, got {type(value).__name__}"
            raise ConstraintViolationError(msg)

        if (
            self.supported_mime_types is not None
            and value.mime_type not in self.supported_mime_types
        ):
            supported_values = [mt.value for mt in self.supported_mime_types]
            got_value = value.mime_type.value if value.mime_type else None
            msg = f"mime_type must be one of {supported_values}, got {got_value!r}"
            raise ConstraintViolationError(msg)

        return value


class AudiosConstraint(Constraint):
    """Constraint for validating audio artifacts list - validates mime_type and count limits."""

    supported_mime_types: list[AudioMimeType] | None = None
    """Supported MIME types."""

    max_count: int | None = None
    """Maximum number of audios."""

    def __call__(self, value: AudioContent) -> list[AudioArtifact]:
        """Validate audio artifact(s) against constraint and normalize to list."""
        # Normalize: if single AudioArtifact is passed, wrap it in a list
        audios = value if isinstance(value, list) else [value]

        if self.max_count is not None and len(audios) > self.max_count:
            msg = f"Must have at most {self.max_count} audio(s), got {len(audios)}"
            raise ConstraintViolationError(msg)

        if self.supported_mime_types is not None:
            for i, aud in enumerate(audios):
                if not isinstance(aud, AudioArtifact):
                    msg = f"Audio {i + 1}: Must be AudioArtifact, got {type(aud).__name__}"
                    raise ConstraintViolationError(msg)
                if aud.mime_type not in self.supported_mime_types:
                    supported_values = [mt.value for mt in self.supported_mime_types]
                    got_value = aud.mime_type.value if aud.mime_type else None
                    msg = (
                        f"Audio {i + 1}: mime_type must be one of {supported_values}, "
                        f"got {got_value!r}"
                    )
                    raise ConstraintViolationError(msg)

        return audios


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
    "VideoConstraint",
    "VideosConstraint",
]
