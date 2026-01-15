"""Configuration for XAI Responses API."""

from enum import StrEnum


class XAIResponsesEndpoint(StrEnum):
    """Endpoints for XAI Responses API."""

    CREATE_RESPONSE = "/v1/responses"
    LIST_MODELS = "/v1/models"
    GET_MODEL = "/v1/models/{model_id}"


BASE_URL = "https://api.x.ai"
