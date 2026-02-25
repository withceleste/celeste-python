"""Gradium TextToSpeech API parameter mappers."""

from typing import Any

from celeste.models import Model
from celeste.parameters import FieldMapper, ParameterMapper
from celeste.types import AudioContent


class VoiceMapper(FieldMapper[AudioContent]):
    """Map voice to Gradium voice_id field."""

    field = "voice_id"


class PaddingBonusMapper(ParameterMapper[AudioContent]):
    """Map padding_bonus to Gradium json_config.padding_bonus field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform padding_bonus into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request.setdefault("json_config", {})["padding_bonus"] = validated_value
        return request


class OutputFormatMapper(FieldMapper[AudioContent]):
    """Map output_format to Gradium output_format field."""

    field = "output_format"


__all__ = [
    "OutputFormatMapper",
    "PaddingBonusMapper",
    "VoiceMapper",
]
