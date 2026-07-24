"""Configuration for Groq Audio API."""

from enum import StrEnum


class GroqAudioEndpoint(StrEnum):
    """Endpoints for Groq Audio API."""

    CREATE_TRANSCRIPTION = "/openai/v1/audio/transcriptions"


BASE_URL = "https://api.groq.com"
