"""Configuration for Ollama Generate API."""

from enum import StrEnum


class OllamaGenerateEndpoint(StrEnum):
    """Endpoints for Ollama Generate API."""

    GENERATE = "/api/generate"


DEFAULT_BASE_URL = "http://localhost:11434"
