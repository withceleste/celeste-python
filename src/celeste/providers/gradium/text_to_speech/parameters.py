"""Gradium TextToSpeech API parameter mappers."""

from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper


class VoiceMapper(ParameterMapper):
    """Map voice to Gradium voice_id field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform voice into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["voice_id"] = validated_value
        return request


class PaddingBonusMapper(ParameterMapper):
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


class OutputFormatMapper(ParameterMapper):
    """Map output_format to Gradium output_format field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform output_format into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["output_format"] = validated_value
        return request


__all__ = [
    "OutputFormatMapper",
    "PaddingBonusMapper",
    "VoiceMapper",
]
