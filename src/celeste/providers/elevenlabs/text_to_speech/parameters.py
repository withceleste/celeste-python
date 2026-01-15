"""ElevenLabs TextToSpeech API parameter mappers."""

from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper


class VoiceMapper(ParameterMapper):
    """Map voice parameter to ElevenLabs URL path.

    Note: Voice ID goes in URL path, not request body.
    This mapper validates the voice_id but the actual URL construction
    happens in _make_request().
    """

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform voice into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is not None:
            request["_voice_id"] = validated_value
        return request


class OutputFormatMapper(ParameterMapper):
    """Map response_format parameter to ElevenLabs output_format field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform response_format into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            request["output_format"] = "mp3_44100_128"
            return request

        request["output_format"] = validated_value
        return request


class SpeedMapper(ParameterMapper):
    """Map speed parameter to ElevenLabs voice_settings.speed field."""

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

        if "voice_settings" not in request:
            request["voice_settings"] = {}

        request["voice_settings"]["speed"] = validated_value
        return request


class LanguageCodeMapper(ParameterMapper):
    """Map language parameter to ElevenLabs language_code field.

    Only supported by eleven_turbo_v2_5 and eleven_flash_v2_5 models.
    """

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform language into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["language_code"] = str(validated_value)
        return request


__all__ = [
    "LanguageCodeMapper",
    "OutputFormatMapper",
    "SpeedMapper",
    "VoiceMapper",
]
