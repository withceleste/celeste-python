"""Configuration for OpenAI Responses API."""

from enum import StrEnum


class OpenAIResponsesEndpoint(StrEnum):
    """Endpoints for OpenAI Responses API."""

    CREATE_RESPONSE = "/v1/responses"
    LIST_MODELS = "/v1/models"
    GET_MODEL = "/v1/models/{model_id}"


BASE_URL = "https://api.openai.com"
