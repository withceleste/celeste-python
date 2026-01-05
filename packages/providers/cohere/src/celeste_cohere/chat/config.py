"""Configuration for Cohere Chat API."""

from enum import StrEnum


class CohereChatEndpoint(StrEnum):
    """Endpoints for Cohere Chat API."""

    CREATE_CHAT = "/v2/chat"
    LIST_MODELS = "/v2/models"
    GET_MODEL = "/v2/models/{model_id}"


BASE_URL = "https://api.cohere.com"
