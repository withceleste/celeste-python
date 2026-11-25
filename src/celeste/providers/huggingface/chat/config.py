"""Configuration for HuggingFace Chat API."""

from enum import StrEnum


class HuggingFaceChatEndpoint(StrEnum):
    """Endpoints for HuggingFace Chat API."""

    CREATE_CHAT_COMPLETION = "/v1/chat/completions"


BASE_URL = "https://router.huggingface.co"
