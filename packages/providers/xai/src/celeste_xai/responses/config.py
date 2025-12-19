"""Configuration for XAI Responses API."""

from enum import StrEnum


class XAIResponsesEndpoint(StrEnum):
    """Endpoints for Responses API."""

    CREATE_RESPONSE = "/v1/responses"


BASE_URL = "https://api.x.ai"
