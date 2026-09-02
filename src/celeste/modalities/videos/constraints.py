"""Constraint models for the videos modality."""

from typing import ClassVar

from celeste.artifacts import ImageArtifact
from celeste.constraints import Constraint
from celeste.exceptions import ConstraintViolationError

from .parameters import VideoKeyframe


class VideoKeyframesConstraint(Constraint):
    """Validate ordered, uniformly timed or untimed video keyframes."""

    _artifact_type: ClassVar[type] = ImageArtifact

    max_count: int
    max_timestamp: float

    def __call__(self, value: object) -> list[VideoKeyframe]:
        """Validate keyframe count, types, and optional timestamps."""
        if not isinstance(value, list) or not value:
            msg = "Must contain at least one VideoKeyframe"
            raise ConstraintViolationError(msg)
        if len(value) > self.max_count:
            msg = f"Must have at most {self.max_count} keyframes, got {len(value)}"
            raise ConstraintViolationError(msg)
        if not all(isinstance(item, VideoKeyframe) for item in value):
            msg = "Every keyframe must be a VideoKeyframe"
            raise ConstraintViolationError(msg)

        keyframes = list(value)
        timestamps = [item.timestamp for item in keyframes]
        timed = [timestamp is not None for timestamp in timestamps]
        if any(timed) and not all(timed):
            msg = "Keyframes must be either all timed or all untimed"
            raise ConstraintViolationError(msg)
        if all(timed):
            numeric = [
                float(timestamp) for timestamp in timestamps if timestamp is not None
            ]
            if any(
                timestamp < 0 or timestamp > self.max_timestamp for timestamp in numeric
            ):
                msg = f"Keyframe timestamps must be between 0 and {self.max_timestamp}"
                raise ConstraintViolationError(msg)
            if numeric != sorted(numeric):
                msg = "Keyframe timestamps must be in ascending order"
                raise ConstraintViolationError(msg)
        return keyframes


__all__ = ["VideoKeyframesConstraint"]
