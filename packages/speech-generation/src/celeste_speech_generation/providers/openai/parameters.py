"""OpenAI parameter mappers for speech generation."""

from typing import Any

from celeste.mime_types import AudioMimeType
from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste_speech_generation.parameters import SpeechGenerationParameter


class VoiceMapper(ParameterMapper):
    """Map voice parameter to OpenAI voice field."""

    name = SpeechGenerationParameter.VOICE

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform voice into provider request.

        Maps the unified voice parameter to the OpenAI API voice field.

        Args:
            request: Provider request dictionary to modify.
            value: The voice ID or name (e.g., 'alloy', 'echo', 'nova').
            model: Model instance with parameter constraints.

        Returns:
            Modified request dictionary with voice parameter.
        """
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["voice"] = validated_value
        return request


class SpeedMapper(ParameterMapper):
    """Map speed parameter to OpenAI speed field."""

    name = SpeechGenerationParameter.SPEED

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform speed into provider request.

        Maps the unified speed parameter to the OpenAI API speed field.
        Valid range is 0.25 to 4.0.

        Args:
            request: Provider request dictionary to modify.
            value: The playback speed multiplier (0.25 to 4.0).
            model: Model instance with parameter constraints.

        Returns:
            Modified request dictionary with speed parameter.
        """
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["speed"] = validated_value
        return request


class ResponseFormatMapper(ParameterMapper):
    """Map response_format parameter to OpenAI response_format field."""

    name = SpeechGenerationParameter.RESPONSE_FORMAT

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform response_format into provider request.

        Maps the unified response_format parameter to the OpenAI API format.
        Accepts both string values ('mp3', 'opus') and AudioMimeType enums.

        Args:
            request: Provider request dictionary to modify.
            value: Output format as string or AudioMimeType (mp3, opus, aac, flac).
            model: Model instance with parameter constraints.

        Returns:
            Modified request dictionary with response_format parameter.
        """
        # Convert string values to AudioMimeType enum before validation
        if isinstance(value, str) and not isinstance(value, AudioMimeType):
            string_to_mime_type: dict[str, AudioMimeType] = {
                "mp3": AudioMimeType.MP3,
                "opus": AudioMimeType.OGG,  # OpenAI uses "opus" for OGG format
                "aac": AudioMimeType.AAC,
                "flac": AudioMimeType.FLAC,
            }
            value = string_to_mime_type.get(value.lower(), value)

        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        # Convert AudioMimeType enum to OpenAI string format
        mime_type_to_openai_format: dict[AudioMimeType, str] = {
            AudioMimeType.MP3: "mp3",
            AudioMimeType.OGG: "opus",  # OpenAI uses "opus" for OGG format
            AudioMimeType.AAC: "aac",
            AudioMimeType.FLAC: "flac",
        }

        # validated_value is now guaranteed to be AudioMimeType after constraint validation
        response_format = mime_type_to_openai_format.get(validated_value, "mp3")
        request["response_format"] = response_format
        return request


OPENAI_PARAMETER_MAPPERS: list[ParameterMapper] = [
    VoiceMapper(),
    SpeedMapper(),
    ResponseFormatMapper(),
]

__all__ = ["OPENAI_PARAMETER_MAPPERS"]
