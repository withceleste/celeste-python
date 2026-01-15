"""Google TTS voice definitions for audio modality."""

from celeste.core import Provider

from ...languages import Language
from ...voices import Voice

# All supported languages for Google Gemini TTS (24 languages, auto-detected)
_SUPPORTED_LANGUAGES = {
    Language.ARABIC,
    Language.GERMAN,
    Language.ENGLISH,
    Language.FRENCH,
    Language.HINDI,
    Language.INDONESIAN,
    Language.ITALIAN,
    Language.JAPANESE,
    Language.KOREAN,
    Language.PORTUGUESE,
    Language.RUSSIAN,
    Language.DUTCH,
    Language.POLISH,
    Language.THAI,
    Language.TURKISH,
    Language.VIETNAMESE,
    Language.ROMANIAN,
    Language.UKRAINIAN,
    Language.TAMIL,
}

# Google Gemini TTS voices (30 voices, all support all languages)
GOOGLE_VOICES = [
    Voice(
        id="Zephyr",
        provider=Provider.GOOGLE,
        name="Zephyr (Bright)",
        languages=_SUPPORTED_LANGUAGES,
    ),
    Voice(
        id="Puck",
        provider=Provider.GOOGLE,
        name="Puck (Upbeat)",
        languages=_SUPPORTED_LANGUAGES,
    ),
    Voice(
        id="Charon",
        provider=Provider.GOOGLE,
        name="Charon (Informative)",
        languages=_SUPPORTED_LANGUAGES,
    ),
    Voice(
        id="Kore",
        provider=Provider.GOOGLE,
        name="Kore (Firm)",
        languages=_SUPPORTED_LANGUAGES,
    ),
    Voice(
        id="Fenrir",
        provider=Provider.GOOGLE,
        name="Fenrir (Excitable)",
        languages=_SUPPORTED_LANGUAGES,
    ),
    Voice(
        id="Leda",
        provider=Provider.GOOGLE,
        name="Leda (Youthful)",
        languages=_SUPPORTED_LANGUAGES,
    ),
    Voice(
        id="Orus",
        provider=Provider.GOOGLE,
        name="Orus (Firm)",
        languages=_SUPPORTED_LANGUAGES,
    ),
    Voice(
        id="Aoede",
        provider=Provider.GOOGLE,
        name="Aoede (Breezy)",
        languages=_SUPPORTED_LANGUAGES,
    ),
    Voice(
        id="Callirrhoe",
        provider=Provider.GOOGLE,
        name="Callirrhoe (Easy-going)",
        languages=_SUPPORTED_LANGUAGES,
    ),
    Voice(
        id="Autonoe",
        provider=Provider.GOOGLE,
        name="Autonoe (Bright)",
        languages=_SUPPORTED_LANGUAGES,
    ),
    Voice(
        id="Enceladus",
        provider=Provider.GOOGLE,
        name="Enceladus (Breathy)",
        languages=_SUPPORTED_LANGUAGES,
    ),
    Voice(
        id="Iapetus",
        provider=Provider.GOOGLE,
        name="Iapetus (Clear)",
        languages=_SUPPORTED_LANGUAGES,
    ),
    Voice(
        id="Umbriel",
        provider=Provider.GOOGLE,
        name="Umbriel (Easy-going)",
        languages=_SUPPORTED_LANGUAGES,
    ),
    Voice(
        id="Algieba",
        provider=Provider.GOOGLE,
        name="Algieba (Smooth)",
        languages=_SUPPORTED_LANGUAGES,
    ),
    Voice(
        id="Despina",
        provider=Provider.GOOGLE,
        name="Despina (Smooth)",
        languages=_SUPPORTED_LANGUAGES,
    ),
    Voice(
        id="Erinome",
        provider=Provider.GOOGLE,
        name="Erinome (Clear)",
        languages=_SUPPORTED_LANGUAGES,
    ),
    Voice(
        id="Algenib",
        provider=Provider.GOOGLE,
        name="Algenib (Gravelly)",
        languages=_SUPPORTED_LANGUAGES,
    ),
    Voice(
        id="Rasalgethi",
        provider=Provider.GOOGLE,
        name="Rasalgethi (Informative)",
        languages=_SUPPORTED_LANGUAGES,
    ),
    Voice(
        id="Laomedeia",
        provider=Provider.GOOGLE,
        name="Laomedeia (Upbeat)",
        languages=_SUPPORTED_LANGUAGES,
    ),
    Voice(
        id="Achernar",
        provider=Provider.GOOGLE,
        name="Achernar (Soft)",
        languages=_SUPPORTED_LANGUAGES,
    ),
    Voice(
        id="Alnilam",
        provider=Provider.GOOGLE,
        name="Alnilam (Firm)",
        languages=_SUPPORTED_LANGUAGES,
    ),
    Voice(
        id="Schedar",
        provider=Provider.GOOGLE,
        name="Schedar (Even)",
        languages=_SUPPORTED_LANGUAGES,
    ),
    Voice(
        id="Gacrux",
        provider=Provider.GOOGLE,
        name="Gacrux (Mature)",
        languages=_SUPPORTED_LANGUAGES,
    ),
    Voice(
        id="Pulcherrima",
        provider=Provider.GOOGLE,
        name="Pulcherrima (Forward)",
        languages=_SUPPORTED_LANGUAGES,
    ),
    Voice(
        id="Achird",
        provider=Provider.GOOGLE,
        name="Achird (Friendly)",
        languages=_SUPPORTED_LANGUAGES,
    ),
    Voice(
        id="Zubenelgenubi",
        provider=Provider.GOOGLE,
        name="Zubenelgenubi (Casual)",
        languages=_SUPPORTED_LANGUAGES,
    ),
    Voice(
        id="Vindemiatrix",
        provider=Provider.GOOGLE,
        name="Vindemiatrix (Gentle)",
        languages=_SUPPORTED_LANGUAGES,
    ),
    Voice(
        id="Sadachbia",
        provider=Provider.GOOGLE,
        name="Sadachbia (Lively)",
        languages=_SUPPORTED_LANGUAGES,
    ),
    Voice(
        id="Sadaltager",
        provider=Provider.GOOGLE,
        name="Sadaltager (Knowledgeable)",
        languages=_SUPPORTED_LANGUAGES,
    ),
    Voice(
        id="Sulafat",
        provider=Provider.GOOGLE,
        name="Sulafat (Warm)",
        languages=_SUPPORTED_LANGUAGES,
    ),
]
