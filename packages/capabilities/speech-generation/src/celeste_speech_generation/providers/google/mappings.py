"""Google TTS parameter mappings."""

from celeste.mime_types import AudioMimeType
from celeste_speech_generation.languages import Language

# Map Language enum values (ISO 639-1) to Google BCP-47 locale codes
LOCALE_MAP: dict[str, str] = {
    Language.ARABIC: "ar-EG",
    Language.GERMAN: "de-DE",
    Language.ENGLISH: "en-US",
    Language.SPANISH: "es-US",
    Language.FRENCH: "fr-FR",
    Language.HINDI: "hi-IN",
    Language.INDONESIAN: "id-ID",
    Language.ITALIAN: "it-IT",
    Language.JAPANESE: "ja-JP",
    Language.KOREAN: "ko-KR",
    Language.PORTUGUESE: "pt-BR",
    Language.RUSSIAN: "ru-RU",
    Language.DUTCH: "nl-NL",
    Language.POLISH: "pl-PL",
    Language.THAI: "th-TH",
    Language.TURKISH: "tr-TR",
    Language.VIETNAMESE: "vi-VN",
    Language.ROMANIAN: "ro-RO",
    Language.UKRAINIAN: "uk-UA",
    Language.TAMIL: "ta-IN",
}

ENCODING_MAP: dict[AudioMimeType, str] = {
    AudioMimeType.MP3: "MP3",
    AudioMimeType.WAV: "LINEAR16",
    AudioMimeType.OGG: "OGG_OPUS",
    AudioMimeType.PCM: "PCM",
}

__all__ = ["ENCODING_MAP", "LOCALE_MAP"]
