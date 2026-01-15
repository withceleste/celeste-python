"""Configuration for OpenAI Images API."""

from enum import StrEnum


class OpenAIImagesEndpoint(StrEnum):
    """Endpoints for OpenAI Images API."""

    CREATE_IMAGE = "/v1/images/generations"
    CREATE_EDIT = "/v1/images/edits"
    CREATE_VARIATION = "/v1/images/variations"


BASE_URL = "https://api.openai.com"
