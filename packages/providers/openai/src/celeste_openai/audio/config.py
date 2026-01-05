"""Configuration for OpenAI Audio API."""

from enum import StrEnum


class OpenAIAudioEndpoint(StrEnum):
    """Endpoints for OpenAI Audio API."""

    CREATE_SPEECH = "/v1/audio/speech"
    CREATE_TRANSCRIPTION = "/v1/audio/transcriptions"
    CREATE_TRANSLATION = "/v1/audio/translations"


BASE_URL = "https://api.openai.com"
