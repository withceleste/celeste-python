"""Ollama provider for images modality."""

from .client import OllamaImagesClient
from .models import MODELS

__all__ = ["MODELS", "OllamaImagesClient"]
