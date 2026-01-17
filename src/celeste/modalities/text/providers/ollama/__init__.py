"""Ollama provider for text modality."""

from .client import OllamaTextClient
from .models import MODELS

__all__ = ["MODELS", "OllamaTextClient"]
