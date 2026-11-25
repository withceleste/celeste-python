"""OpenResponses protocol endpoint configuration."""

from enum import StrEnum


class OpenResponsesEndpoint(StrEnum):
    """Endpoints for the OpenResponses protocol."""

    CREATE_RESPONSE = "/v1/responses"


DEFAULT_BASE_URL = "http://localhost:8000"
