"""Configuration for OpenAI Images API."""

import os
from enum import StrEnum


class OpenAIImagesEndpoint(StrEnum):
    """Endpoints for OpenAI Images API."""

    CREATE_IMAGE = "/v1/images/generations"
    CREATE_EDIT = "/v1/images/edits"
    CREATE_VARIATION = "/v1/images/variations"


# Support custom base URL via environment variable (for OpenAI-compatible APIs)
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com")
