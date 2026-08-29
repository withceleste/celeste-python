"""Configuration for Google Interactions API."""

from enum import StrEnum


class GoogleInteractionsEndpoint(StrEnum):
    """Endpoints for Google Interactions API."""

    # v1beta: /v1 serves only stable models (preview ids 404 there)
    CREATE_INTERACTION = "/v1beta/interactions"


class VertexInteractionsEndpoint(StrEnum):
    """Endpoints for Google Cloud Interactions API."""

    CREATE_INTERACTION = "/v1beta1/projects/{project_id}/locations/global/interactions"


BASE_URL = "https://generativelanguage.googleapis.com"
VERTEX_BASE_URL = "https://aiplatform.googleapis.com"
STORAGE_BASE_URL = "https://storage.googleapis.com/"
FILE_POLL_INTERVAL = 5
FILE_POLL_TIMEOUT = 300
