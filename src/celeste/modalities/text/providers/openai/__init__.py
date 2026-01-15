"""OpenAI provider for text modality."""

from .client import OpenAITextClient
from .models import MODELS

__all__ = ["MODELS", "OpenAITextClient"]
