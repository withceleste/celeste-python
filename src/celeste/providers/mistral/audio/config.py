"""Configuration for Mistral Audio API."""

from enum import StrEnum


class MistralAudioEndpoint(StrEnum):
    """Endpoints for Mistral Audio API."""

    CREATE_TRANSCRIPTION = "/v1/audio/transcriptions"


BASE_URL = "https://api.mistral.ai"
