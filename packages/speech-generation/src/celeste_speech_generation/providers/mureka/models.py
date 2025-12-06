"""Mureka models for speech generation."""

from celeste import Model, Provider
from celeste.constraints import Choice
from celeste_speech_generation.parameters import SpeechGenerationParameter

from .voices import MUREKA_VOICES

# Voice constraint for Mureka TTS
VOICE_CONSTRAINT = Choice(options=["Ethan", "Victoria", "Jake", "Luna", "Emma"])

# Mureka has one TTS model with all voices available
MODELS: list[Model] = [
    Model(
        id="mureka-tts-1",
        provider=Provider.MUREKA,
        display_name="Mureka TTS",
        description="Mureka text-to-speech with multiple voice options",
        streaming=False,  # Mureka TTS returns URLs, not streaming
        voices=MUREKA_VOICES,
        parameter_constraints={
            SpeechGenerationParameter.VOICE: VOICE_CONSTRAINT,
        },
    ),
]

__all__ = ["MODELS"]
