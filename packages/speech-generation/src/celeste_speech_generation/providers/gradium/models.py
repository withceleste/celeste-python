"""Gradium models for speech generation."""

from celeste import Model, Provider
from celeste.constraints import Choice, Range
from celeste_speech_generation.parameters import SpeechGenerationParameter

from . import config
from .voices import GRADIUM_FLAGSHIP_VOICES

# Voice constraint for Gradium TTS (flagship voices)
VOICE_CONSTRAINT = Choice(
    options=[voice.id for voice in GRADIUM_FLAGSHIP_VOICES]
)

# Speed constraint (padding_bonus)
SPEED_CONSTRAINT = Range(min=config.MIN_SPEED, max=config.MAX_SPEED)

# Response format constraint
FORMAT_CONSTRAINT = Choice(options=config.AUDIO_FORMATS)

# Gradium TTS model
MODELS: list[Model] = [
    Model(
        id="default",
        provider=Provider.GRADIUM,
        display_name="Gradium TTS",
        description="Gradium text-to-speech with low-latency streaming and multi-language support",
        streaming=True,  # Gradium supports streaming via WebSocket
        voices=GRADIUM_FLAGSHIP_VOICES,
        parameter_constraints={
            SpeechGenerationParameter.VOICE: VOICE_CONSTRAINT,
            SpeechGenerationParameter.SPEED: SPEED_CONSTRAINT,
            SpeechGenerationParameter.RESPONSE_FORMAT: FORMAT_CONSTRAINT,
        },
    ),
]

__all__ = ["MODELS"]
