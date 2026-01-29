"""Configuration for xAI Images API."""

from enum import StrEnum


class XAIImagesEndpoint(StrEnum):
    """Endpoints for xAI Images API."""

    CREATE_IMAGE = "/v1/images/generations"
    CREATE_EDIT = "/v1/images/edits"


BASE_URL = "https://api.x.ai"
