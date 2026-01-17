"""Configuration for OpenResponses API."""

from enum import StrEnum


class OpenResponsesEndpoint(StrEnum):
    """Endpoints for OpenResponses API."""

    CREATE_RESPONSE = "/v1/responses"
    LIST_MODELS = "/v1/models"


DEFAULT_BASE_URL = "http://localhost:8000"
