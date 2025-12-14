"""Google models for speech generation."""

from celeste import Model, Provider
from celeste.constraints import Str
from celeste_speech_generation.constraints import VoiceConstraint
from celeste_speech_generation.parameters import SpeechGenerationParameter

from .voices import GOOGLE_VOICES

MODELS: list[Model] = [
    Model(
        id="gemini-2.5-flash-preview-tts",
        provider=Provider.GOOGLE,
        display_name="Gemini 2.5 Flash TTS (Preview)",
        streaming=False,
        parameter_constraints={
            SpeechGenerationParameter.VOICE: VoiceConstraint(voices=GOOGLE_VOICES),
            SpeechGenerationParameter.PROMPT: Str(),
        },
    ),
    Model(
        id="gemini-2.5-pro-preview-tts",
        provider=Provider.GOOGLE,
        display_name="Gemini 2.5 Pro TTS (Preview)",
        streaming=False,
        parameter_constraints={
            SpeechGenerationParameter.VOICE: VoiceConstraint(voices=GOOGLE_VOICES),
            SpeechGenerationParameter.PROMPT: Str(),
        },
    ),
]
