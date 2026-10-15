"""Configuration for ElevenLabs Text-to-Speech API."""

from enum import StrEnum


class ElevenLabsTextToSpeechEndpoint(StrEnum):
    """Endpoints for ElevenLabs Text-to-Speech API."""

    CREATE_SPEECH = "/v1/text-to-speech/{voice_id}"
    STREAM_SPEECH = "/v1/text-to-speech/{voice_id}/stream"
    LIST_VOICES = "/v1/voices"
    LIST_MODELS = "/v1/models"


BASE_URL = "https://api.elevenlabs.io"

# Default voice ID (Janet)
DEFAULT_VOICE_ID = "eLDc7xhWxG2FElT3kUTj"
