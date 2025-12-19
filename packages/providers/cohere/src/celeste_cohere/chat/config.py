"""Configuration for Cohere Chat API."""

from enum import StrEnum


class CohereChatEndpoint(StrEnum):
    """Endpoints for Chat API."""

    CREATE_CHAT = "/v2/chat"


BASE_URL = "https://api.cohere.com"
