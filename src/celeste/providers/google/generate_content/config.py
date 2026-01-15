"""Configuration for Google GenerateContent API."""

from enum import StrEnum


class GoogleGenerateContentEndpoint(StrEnum):
    """Endpoints for Google GenerateContent API."""

    GENERATE_CONTENT = "/v1beta/models/{model_id}:generateContent"
    STREAM_GENERATE_CONTENT = "/v1beta/models/{model_id}:streamGenerateContent?alt=sse"
    COUNT_TOKENS = "/v1beta/models/{model_id}:countTokens"
    EMBED_CONTENT = "/v1beta/models/{model_id}:embedContent"
    BATCH_EMBED_CONTENTS = "/v1beta/models/{model_id}:batchEmbedContents"
    LIST_MODELS = "/v1beta/models"
    GET_MODEL = "/v1beta/models/{model_id}"
    UPLOAD_FILE = "/upload/v1beta/files"
    LIST_FILES = "/v1beta/files"
    GET_FILE = "/v1beta/files/{file_id}"
    DELETE_FILE = "/v1beta/files/{file_id}"
    BATCH_GENERATE_CONTENT = "/v1beta/models/{model_id}:batchGenerateContent"


BASE_URL = "https://generativelanguage.googleapis.com"
