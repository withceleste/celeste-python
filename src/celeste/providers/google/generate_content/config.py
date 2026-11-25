"""Configuration for Google GenerateContent API."""

from enum import StrEnum


class GoogleGenerateContentEndpoint(StrEnum):
    """Endpoints for Google GenerateContent API."""

    GENERATE_CONTENT = "/v1beta/models/{model_id}:generateContent"
    STREAM_GENERATE_CONTENT = "/v1beta/models/{model_id}:streamGenerateContent?alt=sse"
    COUNT_TOKENS = "/v1beta/models/{model_id}:countTokens"
    UPLOAD_FILE = "/upload/v1beta/files"
    DELETE_FILE = "/v1beta/files/{file_id}"
    BATCH_GENERATE_CONTENT = "/v1beta/models/{model_id}:batchGenerateContent"


class VertexGenerateContentEndpoint(StrEnum):
    """Endpoints for Vertex AI (when using GoogleADC auth)."""

    GENERATE_CONTENT = "/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model_id}:generateContent"
    STREAM_GENERATE_CONTENT = "/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model_id}:streamGenerateContent?alt=sse"
    COUNT_TOKENS = "/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model_id}:countTokens"


BASE_URL = "https://generativelanguage.googleapis.com"
