"""Configuration for Gradium Text-to-Speech API."""

from enum import StrEnum


class GradiumTextToSpeechEndpoint(StrEnum):
    """Endpoints for Gradium Text-to-Speech API."""

    CREATE_SPEECH = "/speech/tts"


BASE_URL = "wss://eu.api.gradium.ai/api"

# Default voice ID (Emma - English female)
DEFAULT_VOICE_ID = "YTpq7expH9539ERJ"
