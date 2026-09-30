"""Configuration for OpenAI Live API."""

from enum import StrEnum

from celeste.mime_types import AudioMimeType


class OpenAILiveEndpoint(StrEnum):
    """Endpoints for OpenAI Live API."""

    CREATE_SESSION = "/v1/live/sessions"


BASE_URL = "wss://api.openai.com"
DEFAULT_AUDIO_FORMAT = {"type": AudioMimeType.PCM, "rate": 24000}
CLOSE_TIMEOUT = 15.0  # seconds to await session.closed after session.close
