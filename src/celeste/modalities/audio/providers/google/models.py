"""Google TTS models for audio modality."""

from celeste.constraints import Choice
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import AudioMimeType
from celeste.models import Model

from ...constraints import VoiceConstraint
from ...languages import Language
from ...parameters import AudioParameter
from .voices import GOOGLE_VOICES

# Supported output formats for Google TTS
GOOGLE_SUPPORTED_FORMATS = [
    AudioMimeType.MP3,
    AudioMimeType.WAV,
    AudioMimeType.OGG,
    AudioMimeType.PCM,
]

# Supported languages for Google TTS (subset of Language enum)
GOOGLE_SUPPORTED_LANGUAGES = [
    Language.ARABIC,
    Language.GERMAN,
    Language.ENGLISH,
    Language.SPANISH,
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
]

MODELS: list[Model] = [
    Model(
        id="gemini-2.5-flash-tts",
        provider=Provider.GOOGLE,
        display_name="Google TTS Gemini 2.5 Flash",
        streaming=False,
        operations={Modality.AUDIO: {Operation.SPEAK}},
        parameter_constraints={
            AudioParameter.VOICE: VoiceConstraint(voices=GOOGLE_VOICES),
            AudioParameter.LANGUAGE: Choice(options=GOOGLE_SUPPORTED_LANGUAGES),
            AudioParameter.OUTPUT_FORMAT: Choice(options=GOOGLE_SUPPORTED_FORMATS),
        },
    ),
    Model(
        id="gemini-2.5-pro-tts",
        provider=Provider.GOOGLE,
        display_name="Google TTS Gemini 2.5 Pro",
        streaming=False,
        operations={Modality.AUDIO: {Operation.SPEAK}},
        parameter_constraints={
            AudioParameter.VOICE: VoiceConstraint(voices=GOOGLE_VOICES),
            AudioParameter.LANGUAGE: Choice(options=GOOGLE_SUPPORTED_LANGUAGES),
            AudioParameter.OUTPUT_FORMAT: Choice(options=GOOGLE_SUPPORTED_FORMATS),
        },
    ),
]
