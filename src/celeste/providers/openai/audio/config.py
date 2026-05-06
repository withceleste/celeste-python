"""Configuration for OpenAI Audio API."""

import os
from enum import StrEnum


class OpenAIAudioEndpoint(StrEnum):
    """Endpoints for OpenAI Audio API."""

    CREATE_SPEECH = "/v1/audio/speech"
    CREATE_TRANSCRIPTION = "/v1/audio/transcriptions"
    CREATE_TRANSLATION = "/v1/audio/translations"


# Support custom base URL via environment variable (for OpenAI-compatible APIs)
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com")
