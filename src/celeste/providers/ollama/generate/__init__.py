"""Ollama Generate API provider package."""

from .client import OllamaGenerateClient
from .config import DEFAULT_BASE_URL

__all__ = ["DEFAULT_BASE_URL", "OllamaGenerateClient"]
