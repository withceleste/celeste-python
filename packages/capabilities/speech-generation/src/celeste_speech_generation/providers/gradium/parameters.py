"""Gradium Text-to-Speech parameter mappers for speech generation."""

from typing import Any

from celeste_gradium.text_to_speech.parameters import (
    OutputFormatMapper as _OutputFormatMapper,
)
from celeste_gradium.text_to_speech.parameters import (
    PaddingBonusMapper as _PaddingBonusMapper,
)
from celeste_gradium.text_to_speech.parameters import (
    VoiceMapper as _VoiceMapper,
)

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste_speech_generation.parameters import SpeechGenerationParameter


class VoiceMapper(_VoiceMapper):
    name = SpeechGenerationParameter.VOICE


class OutputFormatMapper(_OutputFormatMapper):
    name = SpeechGenerationParameter.OUTPUT_FORMAT


class SpeedMapper(_PaddingBonusMapper):
    """Translate unified speed to Gradium padding_bonus.

    speed 1.0 → padding_bonus 0 (normal)
    speed 0.5 → padding_bonus 2.0 (slower)
    speed 2.0 → padding_bonus -4.0 (faster)
    """

    name = SpeechGenerationParameter.SPEED

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform speed into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        # Translate: speed → padding_bonus
        padding_bonus = (1.0 - validated_value) * 4.0
        return super().map(request, padding_bonus, model)


GRADIUM_PARAMETER_MAPPERS: list[ParameterMapper] = [
    VoiceMapper(),
    OutputFormatMapper(),
    SpeedMapper(),
]

__all__ = ["GRADIUM_PARAMETER_MAPPERS"]
