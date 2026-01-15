"""Configuration for DeepSeek Chat API."""

from enum import StrEnum


class DeepSeekChatEndpoint(StrEnum):
    """Endpoints for DeepSeek Chat API."""

    CREATE_CHAT = "/v1/chat/completions"
    LIST_MODELS = "/models"


BASE_URL = "https://api.deepseek.com"
