"""Google Cloud TTS API parameter mappers."""

from typing import Any, ClassVar

from celeste.mime_types import AudioMimeType
from celeste.models import Model
from celeste.parameters import ParameterMapper


class VoiceMapper(ParameterMapper):
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


class LanguageMapper(ParameterMapper):
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


class PromptMapper(ParameterMapper):
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


class AudioEncodingMapper(ParameterMapper):
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


__all__ = [
    "AudioEncodingMapper",
    "LanguageMapper",
    "PromptMapper",
    "VoiceMapper",
]
