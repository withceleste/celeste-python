"""Configuration for HuggingFace Chat API."""

from enum import StrEnum


class HuggingFaceChatEndpoint(StrEnum):
    """Endpoints for HuggingFace Chat API."""

    CREATE_CHAT_COMPLETION = "/v1/chat/completions"
    LIST_MODELS = "/v1/models"


BASE_URL = "https://router.huggingface.co"
