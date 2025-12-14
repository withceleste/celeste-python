"""OpenAI provider for speech generation."""

from .client import OpenAISpeechGenerationClient
from .models import MODELS

__all__ = ["MODELS", "OpenAISpeechGenerationClient"]
