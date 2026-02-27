"""Google Cloud TTS API parameter mappers."""

from typing import Any, ClassVar

from celeste.artifacts import AudioArtifact
from celeste.mime_types import AudioMimeType
from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.types import AudioContent


class VoiceMapper(ParameterMapper[AudioContent]):
    """Map voice to Google Cloud TTS voice.name field."""

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

        request.setdefault("voice", {})["name"] = validated_value
        return request


class LanguageMapper(ParameterMapper[AudioContent]):
    """Map language to Google Cloud TTS voice.languageCode field."""

    locale_map: ClassVar[dict[str, str]] = {}

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform language into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            request.setdefault("voice", {})["languageCode"] = "fr-FR"
            return request

        # Convert to string (handles both str and StrEnum)
        lang_code = str(validated_value)
        locale_code = self.locale_map.get(lang_code)

        if locale_code:
            request.setdefault("voice", {})["languageCode"] = locale_code

        return request


class PromptMapper(ParameterMapper[AudioContent]):
    """Map prompt to Google Cloud TTS input.prompt field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform prompt into provider request."""
        if not value or not isinstance(value, str):
            return request

        request.setdefault("input", {})["prompt"] = value
        return request


class AudioEncodingMapper(ParameterMapper[AudioContent]):
    """Map audio_encoding to Google Cloud TTS audioConfig.audioEncoding field."""

    encoding_map: ClassVar[dict[AudioMimeType, str]] = {}

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform audio_encoding into provider request."""
        validated_value = self._validate_value(value, model)

        if validated_value is None:
            request.setdefault("audioConfig", {})["audioEncoding"] = "MP3"
            return request

        # Convert to AudioMimeType if string (fail fast if invalid)
        if isinstance(validated_value, str):
            validated_value = AudioMimeType(validated_value)

        # Default to MP3 if mapping fails
        encoding = self.encoding_map.get(validated_value, "MP3")
        request.setdefault("audioConfig", {})["audioEncoding"] = encoding
        return request

    _mime_map: ClassVar[dict[str, AudioMimeType]] = {
        AudioMimeType.MP3: AudioMimeType.MP3,
        AudioMimeType.WAV: AudioMimeType.WAV,
        AudioMimeType.OGG: AudioMimeType.OGG,
        AudioMimeType.PCM: AudioMimeType.PCM,
    }

    def parse_output(self, content: AudioContent, value: object | None) -> AudioContent:
        """Apply output_format → MIME type mapping to parsed content."""
        if not isinstance(content, AudioArtifact):
            return content
        mime_type = self._mime_map.get(str(value) if value else "", AudioMimeType.MP3)
        return AudioArtifact(data=content.data, mime_type=mime_type)


__all__ = [
    "AudioEncodingMapper",
    "LanguageMapper",
    "PromptMapper",
    "VoiceMapper",
]
