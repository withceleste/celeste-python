"""Google parameter mappers for audio modality."""

from typing import Any, ClassVar

from celeste.core import Modality, Operation
from celeste.mime_types import AudioMimeType
from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.providers.google.interactions.parameters import (
    AudioMimeTypeMapper as _AudioMimeTypeMapper,
)
from celeste.providers.google.interactions.parameters import (
    LanguageMapper as _LanguageMapper,
)
from celeste.providers.google.interactions.parameters import (
    MediaContentMapper as _MediaContentMapper,
)
from celeste.providers.google.interactions.parameters import (
    VoiceMapper as _VoiceMapper,
)
from celeste.types import AudioContent

from ...parameters import AudioParameter


class VoiceMapper(_VoiceMapper):
    """Map voice to Google Interactions speech_config voice field."""

    name = AudioParameter.VOICE


class LanguageMapper(_LanguageMapper):
    """Map language to Google Interactions speech_config language field."""

    name = AudioParameter.LANGUAGE
    locale_map: ClassVar[dict[str, str]] = {
        "ar": "ar-EG",
        "de": "de-DE",
        "en": "en-US",
        "es": "es-US",
        "fr": "fr-FR",
        "hi": "hi-IN",
        "id": "id-ID",
        "it": "it-IT",
        "ja": "ja-JP",
        "ko": "ko-KR",
        "pt": "pt-BR",
        "ru": "ru-RU",
        "nl": "nl-NL",
        "pl": "pl-PL",
        "th": "th-TH",
        "tr": "tr-TR",
        "vi": "vi-VN",
        "ro": "ro-RO",
        "uk": "uk-UA",
        "ta": "ta-IN",
        "zh": "cmn-Hans-CN",
        "cs": "cs-CZ",
        "da": "da-DK",
        "fil": "fil-PH",
        "fi": "fi-FI",
        "el": "el-GR",
        "hu": "hu-HU",
        "ms": "ms-MY",
        "no": "nb-NO",
        "sk": "sk-SK",
        "sv": "sv-SE",
    }

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Route language hints to the operation-specific Google config."""
        if Operation.TRANSCRIBE not in model.operations.get(Modality.AUDIO, set()):
            return super().map(request, value, model)

        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request
        locale = self.locale_map.get(str(validated_value), str(validated_value))
        transcription_config = request.setdefault("generation_config", {}).setdefault(
            "transcription_config", {}
        )
        transcription_config["language_codes"] = [locale]
        return request


class OutputFormatMapper(_AudioMimeTypeMapper):
    """Map output_format to Google Interactions response_format.mime_type field."""

    name = AudioParameter.OUTPUT_FORMAT
    mime_map: ClassVar[dict[AudioMimeType, str]] = {
        AudioMimeType.MP3: "audio/mp3",
        AudioMimeType.WAV: "audio/wav",
        AudioMimeType.OGG: "audio/ogg_opus",
        AudioMimeType.PCM: "audio/l16",
    }


class ReferenceImagesMapper(_MediaContentMapper[AudioContent]):
    """Map reference_images to Google Interactions input content."""

    name = AudioParameter.REFERENCE_IMAGES


GOOGLE_PARAMETER_MAPPERS: list[ParameterMapper[AudioContent]] = [
    VoiceMapper(),
    LanguageMapper(),
    OutputFormatMapper(),
    ReferenceImagesMapper(),
]

__all__ = ["GOOGLE_PARAMETER_MAPPERS"]
