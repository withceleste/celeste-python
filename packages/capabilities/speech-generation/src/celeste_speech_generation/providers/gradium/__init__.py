"""Gradium provider for speech generation."""

from .client import GradiumSpeechGenerationClient
from .models import MODELS

__all__ = [
    "MODELS",
    "GradiumSpeechGenerationClient",
]
