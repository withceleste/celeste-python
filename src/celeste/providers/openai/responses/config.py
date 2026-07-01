"""Configuration for OpenAI Responses API."""

import os
from enum import StrEnum


class OpenAIResponsesEndpoint(StrEnum):
    """Endpoints for OpenAI Responses API."""

    CREATE_RESPONSE = "/v1/responses"
    LIST_MODELS = "/v1/models"
    GET_MODEL = "/v1/models/{model_id}"


# Support custom base URL via environment variable (for OpenAI-compatible APIs)
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com")
