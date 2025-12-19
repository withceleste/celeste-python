"""Language definitions for speech generation."""

from enum import StrEnum


class Language(StrEnum):
    """ISO 639-1 language codes for speech generation.

    Values are ISO 639-1 codes, allowing both enum and string usage:
    - `Language.ENGLISH` → "en"
    - `"en"` → works directly
    """

    ARABIC = "ar"
    CHINESE = "zh"
    CZECH = "cs"
    DANISH = "da"
    DUTCH = "nl"
    ENGLISH = "en"
    FILIPINO = "fil"
    FINNISH = "fi"
    FRENCH = "fr"
    GERMAN = "de"
    GREEK = "el"
    HINDI = "hi"
    HUNGARIAN = "hu"
    INDONESIAN = "id"
    ITALIAN = "it"
    JAPANESE = "ja"
    KOREAN = "ko"
    MALAY = "ms"
    NORWEGIAN = "no"
    POLISH = "pl"
    PORTUGUESE = "pt"
    ROMANIAN = "ro"
    RUSSIAN = "ru"
    SLOVAK = "sk"
    SPANISH = "es"
    SWEDISH = "sv"
    TAMIL = "ta"
    THAI = "th"
    TURKISH = "tr"
    UKRAINIAN = "uk"
    VIETNAMESE = "vi"


__all__ = ["Language"]
