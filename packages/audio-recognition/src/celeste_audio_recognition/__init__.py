"""Audio recognition (Speech-to-Text) capabilities for Celeste AI."""

from celeste_audio_recognition.client import AudioRecognitionClient
from celeste_audio_recognition.io import (
    AudioRecognitionChunk,
    AudioRecognitionInput,
    AudioRecognitionOutput,
    AudioRecognitionUsage,
)
from celeste_audio_recognition.parameters import (
    AudioRecognitionParameter,
    AudioRecognitionParameters,
)


def register_package() -> None:
    """Register audio recognition models and providers.

    This function is called by Celeste's entry point system.
    """
    from celeste.client import register_client
    from celeste.core import Capability
    from celeste.models import register_models

    from celeste_audio_recognition.models import MODELS
    from celeste_audio_recognition.providers import PROVIDERS

    # Register all clients
    for provider, client_class in PROVIDERS:
        register_client(Capability.AUDIO_RECOGNITION, provider, client_class)

    # Register all models
    register_models(MODELS, capability=Capability.AUDIO_RECOGNITION)


__all__ = [
    "AudioRecognitionChunk",
    "AudioRecognitionClient",
    "AudioRecognitionInput",
    "AudioRecognitionOutput",
    "AudioRecognitionParameter",
    "AudioRecognitionParameters",
    "AudioRecognitionUsage",
    "register_package",
]
