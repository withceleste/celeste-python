"""Google parameter mappers for audio modality."""

from typing import ClassVar

from celeste.mime_types import AudioMimeType
from celeste.parameters import ParameterMapper
from celeste.providers.google.cloud_tts.parameters import (
    AudioEncodingMapper as _AudioEncodingMapper,
)
from celeste.providers.google.cloud_tts.parameters import (
    LanguageMapper as _LanguageMapper,
)
from celeste.providers.google.cloud_tts.parameters import (
    VoiceMapper as _VoiceMapper,
)

from ...parameters import AudioParameter


class VoiceMapper(_VoiceMapper):
    """Map voice to Google Cloud TTS voice.name field."""

    name = AudioParameter.VOICE


class LanguageMapper(_LanguageMapper):
    """Map language to Google Cloud TTS voice.languageCode field."""

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
    }


class OutputFormatMapper(_AudioEncodingMapper):
    """Map output_format to Google Cloud TTS audioConfig.audioEncoding field."""

    name = AudioParameter.OUTPUT_FORMAT
    encoding_map: ClassVar[dict[AudioMimeType, str]] = {
        AudioMimeType.MP3: "MP3",
        AudioMimeType.WAV: "LINEAR16",
        AudioMimeType.OGG: "OGG_OPUS",
        AudioMimeType.PCM: "PCM",
    }


GOOGLE_PARAMETER_MAPPERS: list[ParameterMapper] = [
    VoiceMapper(),
    LanguageMapper(),
    OutputFormatMapper(),
]

__all__ = ["GOOGLE_PARAMETER_MAPPERS"]
