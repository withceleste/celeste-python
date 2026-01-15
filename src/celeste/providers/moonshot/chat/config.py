"""Configuration for Moonshot Chat API."""

from enum import StrEnum


class MoonshotChatEndpoint(StrEnum):
    """Endpoints for Moonshot Chat API."""

    CREATE_CHAT = "/v1/chat/completions"


BASE_URL = "https://api.moonshot.ai"
