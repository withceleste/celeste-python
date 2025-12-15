"""Configuration for OpenAI Responses API."""

from enum import StrEnum


class OpenAIResponsesEndpoint(StrEnum):
    """Endpoints for Responses API."""

    CREATE_RESPONSE = "/v1/responses"


BASE_URL = "https://api.openai.com"
