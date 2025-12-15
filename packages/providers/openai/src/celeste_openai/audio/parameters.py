"""OpenAI Audio API parameter mappers."""

from typing import Any

from celeste.mime_types import AudioMimeType
from celeste.models import Model
from celeste.parameters import ParameterMapper


class VoiceMapper(ParameterMapper):
    """Map voice to OpenAI voice field."""

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

        request["voice"] = validated_value
        return request


class SpeedMapper(ParameterMapper):
    """Map speed to OpenAI speed field."""

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

        request["speed"] = validated_value
        return request


class ResponseFormatMapper(ParameterMapper):
    """Map response_format to OpenAI response_format field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform response_format into provider request."""
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

        response_format = mime_type_to_openai_format.get(validated_value, "mp3")
        request["response_format"] = response_format
        return request


class InstructionsMapper(ParameterMapper):
    """Map instructions to OpenAI instructions field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform instructions into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["instructions"] = validated_value
        return request


__all__ = [
    "InstructionsMapper",
    "ResponseFormatMapper",
    "SpeedMapper",
    "VoiceMapper",
]
