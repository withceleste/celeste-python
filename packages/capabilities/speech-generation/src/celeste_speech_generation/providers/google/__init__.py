"""Google provider for speech generation."""

from .client import GoogleSpeechGenerationClient
from .models import MODELS

__all__ = ["MODELS", "GoogleSpeechGenerationClient"]
