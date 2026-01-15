"""Configuration for Google Imagen API."""

from enum import StrEnum


class GoogleImagenEndpoint(StrEnum):
    """Endpoints for Google Imagen API."""

    CREATE_IMAGE = "/v1beta/models/{model_id}:predict"


BASE_URL = "https://generativelanguage.googleapis.com"
