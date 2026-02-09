"""Configuration for Google Veo API."""

from enum import StrEnum


class GoogleVeoEndpoint(StrEnum):
    """Endpoints for Google Veo API."""

    CREATE_VIDEO = "/v1beta/models/{model_id}:predictLongRunning"
    GET_OPERATION = "/v1beta/{operation_name}"


class VertexVeoEndpoint(StrEnum):
    """Endpoints for Veo on Vertex AI."""

    CREATE_VIDEO = "/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model_id}:predictLongRunning"
    FETCH_OPERATION = "/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model_id}:fetchPredictOperation"


BASE_URL = "https://generativelanguage.googleapis.com"

# Polling Configuration
POLL_INTERVAL = 10  # seconds
DEFAULT_TIMEOUT = 300.0  # 5 minutes for long-running operations

# Storage Configuration
STORAGE_BASE_URL = "https://storage.googleapis.com/"
