"""OpenAI provider for audio modality."""

from .client import OpenAIAudioClient
from .models import MODELS

__all__ = ["MODELS", "OpenAIAudioClient"]
