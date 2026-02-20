"""Chat Completions protocol endpoint configuration."""

from enum import StrEnum


class ChatCompletionsEndpoint(StrEnum):
    """Endpoints for the Chat Completions protocol."""

    CREATE_CHAT = "/v1/chat/completions"


DEFAULT_BASE_URL = "http://localhost:8000"
