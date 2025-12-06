"""Model registry for audio recognition."""

from celeste import Model
from celeste_audio_recognition.providers.gradium.models import MODELS as GRADIUM_MODELS

# Unified model registry for all audio recognition providers
MODELS: list[Model] = [
    *GRADIUM_MODELS,
]

__all__ = ["MODELS"]
