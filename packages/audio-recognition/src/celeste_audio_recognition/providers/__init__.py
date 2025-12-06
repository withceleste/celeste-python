"""Provider registration for audio recognition."""

from celeste import Provider
from celeste.client import Client
from celeste_audio_recognition.providers.gradium.client import (
    GradiumAudioRecognitionClient,
)

PROVIDERS: list[tuple[Provider, type[Client]]] = [
    (Provider.GRADIUM, GradiumAudioRecognitionClient),
]

__all__ = ["PROVIDERS"]
