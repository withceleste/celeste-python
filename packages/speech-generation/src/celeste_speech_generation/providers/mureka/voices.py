"""Mureka voice definitions."""

from celeste_speech_generation.voices import Voice

# Predefined Mureka voices based on API documentation
MUREKA_VOICES: list[Voice] = [
    Voice(id="Ethan", name="Ethan", provider="mureka"),
    Voice(id="Victoria", name="Victoria", provider="mureka"),
    Voice(id="Jake", name="Jake", provider="mureka"),
    Voice(id="Luna", name="Luna", provider="mureka"),
    Voice(id="Emma", name="Emma", provider="mureka"),
]

__all__ = ["MUREKA_VOICES"]
