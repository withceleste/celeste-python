"""Gradium models for audio recognition (STT)."""

from celeste import Capability, Model, Provider
from celeste.constraints import Choice
from celeste_audio_recognition.parameters import AudioRecognitionParameter

from . import config

# Input format constraint
INPUT_FORMAT_CONSTRAINT = Choice(options=config.AUDIO_FORMATS)

# Gradium STT model
MODELS: list[Model] = [
    Model(
        id="default",
        provider=Provider.GRADIUM,
        display_name="Gradium STT",
        capabilities={Capability.AUDIO_RECOGNITION},
        streaming=True,  # Supports streaming via WebSocket
        parameter_constraints={
            AudioRecognitionParameter.INPUT_FORMAT: INPUT_FORMAT_CONSTRAINT,
        },
    ),
]

__all__ = ["MODELS"]
