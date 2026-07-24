"""Configuration for ElevenLabs Speech-to-Text API."""

from enum import StrEnum


class ElevenLabsSpeechToTextEndpoint(StrEnum):
    """Endpoints for ElevenLabs Speech-to-Text API."""

    CREATE_TRANSCRIPTION = "/v1/speech-to-text"


BASE_URL = "https://api.elevenlabs.io"
