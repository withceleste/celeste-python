"""Google TTS voice definitions for audio modality."""

from celeste.core import Provider

from ...languages import Language
from ...voices import Voice

# Language metadata shared across Google Gemini TTS voices (auto-detected).
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

# Snapshot 2026-07-14: 30 prebuilt voices.
# Source: https://ai.google.dev/gemini-api/docs/speech-generation#voices
GOOGLE_VOICES = [
    Voice(
        id=name,
        provider=Provider.GOOGLE,
        name=name,
        description=description,
        languages=_SUPPORTED_LANGUAGES,
    )
    for name, description in [
        ("Zephyr", "Bright"),
        ("Puck", "Upbeat"),
        ("Charon", "Informative"),
        ("Kore", "Firm"),
        ("Fenrir", "Excitable"),
        ("Leda", "Youthful"),
        ("Orus", "Firm"),
        ("Aoede", "Breezy"),
        ("Callirrhoe", "Easy-going"),
        ("Autonoe", "Bright"),
        ("Enceladus", "Breathy"),
        ("Iapetus", "Clear"),
        ("Umbriel", "Easy-going"),
        ("Algieba", "Smooth"),
        ("Despina", "Smooth"),
        ("Erinome", "Clear"),
        ("Algenib", "Gravelly"),
        ("Rasalgethi", "Informative"),
        ("Laomedeia", "Upbeat"),
        ("Achernar", "Soft"),
        ("Alnilam", "Firm"),
        ("Schedar", "Even"),
        ("Gacrux", "Mature"),
        ("Pulcherrima", "Forward"),
        ("Achird", "Friendly"),
        ("Zubenelgenubi", "Casual"),
        ("Vindemiatrix", "Gentle"),
        ("Sadachbia", "Lively"),
        ("Sadaltager", "Knowledgeable"),
        ("Sulafat", "Warm"),
    ]
]
