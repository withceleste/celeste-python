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
        "wav": AudioMimeType.WAV,
        "pcm": AudioMimeType.PCM,
    }

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform response_format into provider request."""
        if isinstance(value, str):
            value = self._mime_map.get(value.lower(), value)

        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        mime_type_to_openai_format = {
            mime: output_format for output_format, mime in self._mime_map.items()
        }

        response_format = mime_type_to_openai_format.get(validated_value, "mp3")
        request["response_format"] = response_format
        return request

    def parse_output(self, content: AudioContent, value: object | None) -> AudioContent:
        """Apply response_format → MIME type mapping to parsed content."""
        if not isinstance(content, AudioArtifact) or content.mime_type is not None:
            return content
        output_format = str(value).lower() if value is not None else ""
        mime_type = next(
            (
                mime
                for wire, mime in self._mime_map.items()
                if output_format in (wire, mime)
            ),
            AudioMimeType.MP3,
        )
        return content.model_copy(update={"mime_type": mime_type})


class InstructionsMapper(FieldMapper[AudioContent]):
    """Map instructions to OpenAI instructions field."""

    field = "instructions"


class LanguageMapper[Content](ParameterMapper[Content]):
    """Map language to OpenAI transcription language field."""

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
        request["language"] = validated_value
        return request


class PromptMapper[Content](ParameterMapper[Content]):
    """Map prompt to OpenAI transcription prompt field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform prompt into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request
        request["prompt"] = validated_value
        return request


class TemperatureMapper[Content](ParameterMapper[Content]):
    """Map temperature to OpenAI transcription temperature field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform temperature into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request
        request["temperature"] = validated_value
        return request


__all__ = [
    "InstructionsMapper",
    "LanguageMapper",
    "PromptMapper",
    "ResponseFormatMapper",
    "SpeedMapper",
    "TemperatureMapper",
    "VoiceMapper",
]
