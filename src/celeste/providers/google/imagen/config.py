"""Configuration for Google Imagen API."""

from enum import StrEnum


class GoogleImagenEndpoint(StrEnum):
    """Endpoints for Google Imagen API."""

    CREATE_IMAGE = "/v1beta/models/{model_id}:predict"


class VertexImagenEndpoint(StrEnum):
    """Endpoints for Imagen on Vertex AI."""

    CREATE_IMAGE = "/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model_id}:predict"


BASE_URL = "https://generativelanguage.googleapis.com"
