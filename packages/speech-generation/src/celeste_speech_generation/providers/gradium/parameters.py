"""Gradium parameter mappers for speech generation."""

from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste_speech_generation.parameters import SpeechGenerationParameter


class VoiceMapper(ParameterMapper):
    """Map voice parameter to Gradium voice_id field."""

    name = SpeechGenerationParameter.VOICE

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform voice into provider request.

        Maps the unified voice parameter to the Gradium API voice_id field.
        Supports both flagship voices and custom voice IDs.

        Args:
            request: Provider request dictionary to modify.
            value: The voice ID (e.g., 'YTpq7expH9539ERJ' for Emma).
            model: Model instance with parameter constraints.

        Returns:
            Modified request dictionary with voice_id parameter.
        """
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["voice_id"] = validated_value
        return request


class SpeedMapper(ParameterMapper):
    """Map speed parameter to Gradium padding_bonus field."""

    name = SpeechGenerationParameter.SPEED

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform speed into provider request.

        Maps the unified speed parameter to Gradium's padding_bonus field.
        Range: -4.0 (faster) to 4.0 (slower), default: 0.0

        Args:
            request: Provider request dictionary to modify.
            value: Speed modifier (-4.0 to 4.0).
            model: Model instance with parameter constraints.

        Returns:
            Modified request dictionary with json_config.padding_bonus parameter.
        """
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        # Create json_config if it doesn't exist
        if "json_config" not in request:
            request["json_config"] = {}

        request["json_config"]["padding_bonus"] = float(validated_value)
        return request


class ResponseFormatMapper(ParameterMapper):
    """Map response_format parameter to Gradium output_format field."""

    name = SpeechGenerationParameter.RESPONSE_FORMAT

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform response_format into provider request.

        Maps the unified response_format parameter to the Gradium API output_format field.
        Supported formats: wav, pcm, opus, ulaw_8000, alaw_8000, pcm_16000, pcm_24000

        Args:
            request: Provider request dictionary to modify.
            value: Output format (e.g., 'wav', 'pcm', 'opus').
            model: Model instance with parameter constraints.

        Returns:
            Modified request dictionary with output_format parameter.
        """
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["output_format"] = str(validated_value)
        return request


GRADIUM_PARAMETER_MAPPERS: list[ParameterMapper] = [
    VoiceMapper(),
    SpeedMapper(),
    ResponseFormatMapper(),
]

__all__ = ["GRADIUM_PARAMETER_MAPPERS"]
