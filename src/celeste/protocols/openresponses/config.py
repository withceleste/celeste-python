"""OpenResponses protocol endpoint configuration."""

from enum import StrEnum


class OpenResponsesEndpoint(StrEnum):
    """Endpoints for the OpenResponses protocol."""

    CREATE_RESPONSE = "/v1/responses"
    LIST_MODELS = "/v1/models"


DEFAULT_BASE_URL = "http://localhost:8000"
