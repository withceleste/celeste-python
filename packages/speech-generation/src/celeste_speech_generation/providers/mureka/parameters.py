"""Mureka parameter mappers for speech generation."""

from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste_speech_generation.parameters import SpeechGenerationParameter


class VoiceMapper(ParameterMapper):
    """Map voice parameter to Mureka voice field."""

    name = SpeechGenerationParameter.VOICE

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform voice into provider request.

        Maps the unified voice parameter to the Mureka API voice field.
        Supports both predefined voices (Ethan, Victoria, Jake, Luna, Emma)
        and custom voice IDs via voice_id parameter.

        Args:
            request: Provider request dictionary to modify.
            value: The voice ID or name (e.g., 'Emma', 'Luna').
            model: Model instance with parameter constraints.

        Returns:
            Modified request dictionary with voice parameter.
        """
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["voice"] = validated_value
        return request


MUREKA_PARAMETER_MAPPERS: list[ParameterMapper] = [
    VoiceMapper(),
]

__all__ = ["MUREKA_PARAMETER_MAPPERS"]
