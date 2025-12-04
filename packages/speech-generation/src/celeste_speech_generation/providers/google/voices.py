"""Google voice definitions for speech generation."""

from celeste import Provider
from celeste_speech_generation.voices import Voice

# All Google Gemini voices support all 24 languages
GOOGLE_LANGUAGES = {
    "ar-EG",
    "de-DE",
    "en-US",
    "es-US",
    "fr-FR",
    "hi-IN",
    "id-ID",
    "it-IT",
    "ja-JP",
    "ko-KR",
    "pt-BR",
    "ru-RU",
    "nl-NL",
    "pl-PL",
    "th-TH",
    "tr-TR",
    "vi-VN",
    "ro-RO",
    "uk-UA",
    "bn-BD",
    "en-IN",
    "mr-IN",
    "ta-IN",
    "te-IN",
}

GOOGLE_VOICES = [
    Voice(
        id="Zephyr", provider=Provider.GOOGLE, name="Zephyr", languages=GOOGLE_LANGUAGES
    ),
    Voice(id="Puck", provider=Provider.GOOGLE, name="Puck", languages=GOOGLE_LANGUAGES),
    Voice(
        id="Charon", provider=Provider.GOOGLE, name="Charon", languages=GOOGLE_LANGUAGES
    ),
    Voice(id="Kore", provider=Provider.GOOGLE, name="Kore", languages=GOOGLE_LANGUAGES),
    Voice(
        id="Fenrir", provider=Provider.GOOGLE, name="Fenrir", languages=GOOGLE_LANGUAGES
    ),
    Voice(id="Leda", provider=Provider.GOOGLE, name="Leda", languages=GOOGLE_LANGUAGES),
    Voice(id="Orus", provider=Provider.GOOGLE, name="Orus", languages=GOOGLE_LANGUAGES),
    Voice(
        id="Aoede", provider=Provider.GOOGLE, name="Aoede", languages=GOOGLE_LANGUAGES
    ),
    Voice(
        id="Callirrhoe",
        provider=Provider.GOOGLE,
        name="Callirrhoe",
        languages=GOOGLE_LANGUAGES,
    ),
    Voice(
        id="Autonoe",
        provider=Provider.GOOGLE,
        name="Autonoe",
        languages=GOOGLE_LANGUAGES,
    ),
    Voice(
        id="Enceladus",
        provider=Provider.GOOGLE,
        name="Enceladus",
        languages=GOOGLE_LANGUAGES,
    ),
    Voice(
        id="Iapetus",
        provider=Provider.GOOGLE,
        name="Iapetus",
        languages=GOOGLE_LANGUAGES,
    ),
    Voice(
        id="Umbriel",
        provider=Provider.GOOGLE,
        name="Umbriel",
        languages=GOOGLE_LANGUAGES,
    ),
    Voice(
        id="Algieba",
        provider=Provider.GOOGLE,
        name="Algieba",
        languages=GOOGLE_LANGUAGES,
    ),
    Voice(
        id="Despina",
        provider=Provider.GOOGLE,
        name="Despina",
        languages=GOOGLE_LANGUAGES,
    ),
    Voice(
        id="Erinome",
        provider=Provider.GOOGLE,
        name="Erinome",
        languages=GOOGLE_LANGUAGES,
    ),
    Voice(
        id="Algenib",
        provider=Provider.GOOGLE,
        name="Algenib",
        languages=GOOGLE_LANGUAGES,
    ),
    Voice(
        id="Rasalgethi",
        provider=Provider.GOOGLE,
        name="Rasalgethi",
        languages=GOOGLE_LANGUAGES,
    ),
    Voice(
        id="Laomedeia",
        provider=Provider.GOOGLE,
        name="Laomedeia",
        languages=GOOGLE_LANGUAGES,
    ),
    Voice(
        id="Achernar",
        provider=Provider.GOOGLE,
        name="Achernar",
        languages=GOOGLE_LANGUAGES,
    ),
    Voice(
        id="Alnilam",
        provider=Provider.GOOGLE,
        name="Alnilam",
        languages=GOOGLE_LANGUAGES,
    ),
    Voice(
        id="Schedar",
        provider=Provider.GOOGLE,
        name="Schedar",
        languages=GOOGLE_LANGUAGES,
    ),
    Voice(
        id="Gacrux", provider=Provider.GOOGLE, name="Gacrux", languages=GOOGLE_LANGUAGES
    ),
    Voice(
        id="Pulcherrima",
        provider=Provider.GOOGLE,
        name="Pulcherrima",
        languages=GOOGLE_LANGUAGES,
    ),
    Voice(
        id="Achird", provider=Provider.GOOGLE, name="Achird", languages=GOOGLE_LANGUAGES
    ),
    Voice(
        id="Zubenelgenubi",
        provider=Provider.GOOGLE,
        name="Zubenelgenubi",
        languages=GOOGLE_LANGUAGES,
    ),
    Voice(
        id="Vindemiatrix",
        provider=Provider.GOOGLE,
        name="Vindemiatrix",
        languages=GOOGLE_LANGUAGES,
    ),
    Voice(
        id="Sadachbia",
        provider=Provider.GOOGLE,
        name="Sadachbia",
        languages=GOOGLE_LANGUAGES,
    ),
    Voice(
        id="Sadaltager",
        provider=Provider.GOOGLE,
        name="Sadaltager",
        languages=GOOGLE_LANGUAGES,
    ),
    Voice(
        id="Sulafat",
        provider=Provider.GOOGLE,
        name="Sulafat",
        languages=GOOGLE_LANGUAGES,
    ),
]
