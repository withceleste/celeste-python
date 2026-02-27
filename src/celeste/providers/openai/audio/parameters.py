"""OpenAI Audio API parameter mappers."""

from typing import Any, ClassVar

from celeste.artifacts import AudioArtifact
from celeste.mime_types import AudioMimeType
from celeste.models import Model
from celeste.parameters import FieldMapper, ParameterMapper
from celeste.types import AudioContent


class VoiceMapper(FieldMapper[AudioContent]):
    """Map voice to OpenAI voice field."""

    field = "voice"


class SpeedMapper(FieldMapper[AudioContent]):
    """Map speed to OpenAI speed field."""

    field = "speed"


class ResponseFormatMapper(ParameterMapper[AudioContent]):
    """Map response_format to OpenAI response_format field."""

    _mime_map: ClassVar[dict[str, AudioMimeType]] = {
        "mp3": AudioMimeType.MP3,
        "opus": AudioMimeType.OGG,
        "aac": AudioMimeType.AAC,
        "flac": AudioMimeType.FLAC,
    }

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

    def parse_output(self, content: AudioContent, value: object | None) -> AudioContent:
        """Apply response_format → MIME type mapping to parsed content."""
        if not isinstance(content, AudioArtifact):
            return content
        mime_type = self._mime_map.get(str(value) if value else "", AudioMimeType.MP3)
        return AudioArtifact(data=content.data, mime_type=mime_type)


class InstructionsMapper(FieldMapper[AudioContent]):
    """Map instructions to OpenAI instructions field."""

    field = "instructions"


__all__ = [
    "InstructionsMapper",
    "ResponseFormatMapper",
    "SpeedMapper",
    "VoiceMapper",
]
