"""Gradium model definitions for speech generation."""

from celeste import Model, Provider
from celeste.constraints import Choice, Range
from celeste_speech_generation.constraints import VoiceConstraint
from celeste_speech_generation.parameters import SpeechGenerationParameter

from .voices import GRADIUM_VOICES

MODELS: list[Model] = [
    Model(
        id="default",
        provider=Provider.GRADIUM,
        display_name="Gradium Default TTS",
        streaming=False,
        parameter_constraints={
            SpeechGenerationParameter.VOICE: VoiceConstraint(voices=GRADIUM_VOICES),
            SpeechGenerationParameter.OUTPUT_FORMAT: Choice(
                options=[
                    "wav",
                    "pcm",
                    "opus",
                    "ulaw_8000",
                    "alaw_8000",
                    "pcm_16000",
                    "pcm_24000",
                ]
            ),
            SpeechGenerationParameter.SPEED: Range(min=0.25, max=4.0),
        },
    ),
]

__all__ = ["MODELS"]
