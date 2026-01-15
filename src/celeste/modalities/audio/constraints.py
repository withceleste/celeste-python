"""Constraint models for audio modality."""

from pydantic import Field

from celeste.constraints import Constraint
from celeste.exceptions import ConstraintViolationError

from .voices import Voice


class VoiceConstraint(Constraint):
    """Voice constraint - value must be a valid voice ID from the provided voices.

    Accepts either voice ID or voice name and returns the canonical voice ID.
    """

    voices: list[Voice] = Field(min_length=1)
    """List of valid voices for this constraint."""

    def __call__(self, value: str) -> str:
        """Validate value is a valid voice ID or name and return the ID."""
        if not isinstance(value, str):
            msg = f"Must be string, got {type(value).__name__}"
            raise ConstraintViolationError(msg)

        # Check if value is a voice ID
        voice_ids = [v.id for v in self.voices]
        if value in voice_ids:
            return value

        # Check if value is a voice name and return corresponding ID
        voice_name_to_id = {v.name: v.id for v in self.voices}
        if value in voice_name_to_id:
            return voice_name_to_id[value]

        # Neither ID nor name matches
        voice_names = [v.name for v in self.voices]
        msg = (
            f"Must be one of {voice_names} (names) or {voice_ids} (IDs), got {value!r}"
        )
        raise ConstraintViolationError(msg)


__all__ = ["VoiceConstraint"]
