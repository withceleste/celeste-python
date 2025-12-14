"""ElevenLabs parameter mappers for speech generation."""

from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste_speech_generation.parameters import SpeechGenerationParameter


class VoiceMapper(ParameterMapper):
    """Map voice parameter to ElevenLabs URL path.

    Note: Voice ID goes in URL path, not request body.
    This mapper validates the voice_id but the actual URL construction
    happens in _make_request().
    """

    name = SpeechGenerationParameter.VOICE

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Validate and store voice ID for URL construction.

        ElevenLabs requires voice_id in the URL path, not the request body.
        This mapper validates the voice_id and stores it in the request dict
        under '_voice_id' for later use in _make_request().

        Args:
            request: Provider request dictionary to modify.
            value: The voice ID or name (e.g., 'Rachel', '21m00Tcm4TlvDq8ikWAM').
            model: Model instance with parameter constraints.

        Returns:
            Modified request dictionary with _voice_id key.
        """
        validated_value = self._validate_value(value, model)
        # Voice ID is stored in request for later use in _make_request()
        # but not added to request body
        if validated_value is not None:
            request["_voice_id"] = validated_value
        return request


class OutputFormatMapper(ParameterMapper):
    """Map response_format parameter to ElevenLabs output_format field."""

    name = SpeechGenerationParameter.RESPONSE_FORMAT

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform response_format into provider request.

        Maps the unified response_format parameter to ElevenLabs output_format.
        Defaults to 'mp3_44100_128' if not provided.

        Args:
            request: Provider request dictionary to modify.
            value: Output format string (e.g., 'mp3_44100_128', 'pcm_22050_16').
            model: Model instance with parameter constraints.

        Returns:
            Modified request dictionary with output_format parameter.
        """
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            # Default to mp3_44100_128 if not provided
            request["output_format"] = "mp3_44100_128"
            return request

        request["output_format"] = validated_value
        return request


class SpeedMapper(ParameterMapper):
    """Map speed parameter to ElevenLabs voice_settings.speed field."""

    name = SpeechGenerationParameter.SPEED

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform speed into provider request.

        Maps the unified speed parameter to ElevenLabs voice_settings.speed.
        Valid range is 0.7 to 1.2 for ElevenLabs models.

        Args:
            request: Provider request dictionary to modify.
            value: The playback speed multiplier (0.7 to 1.2).
            model: Model instance with parameter constraints.

        Returns:
            Modified request dictionary with voice_settings.speed parameter.
        """
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        # Ensure voice_settings object exists
        if "voice_settings" not in request:
            request["voice_settings"] = {}

        request["voice_settings"]["speed"] = validated_value
        return request


ELEVENLABS_PARAMETER_MAPPERS: list[ParameterMapper] = [
    VoiceMapper(),
    OutputFormatMapper(),
    SpeedMapper(),
]

__all__ = ["ELEVENLABS_PARAMETER_MAPPERS"]
