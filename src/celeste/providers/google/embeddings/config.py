"""Configuration for Google Embeddings API."""

from enum import StrEnum


class GoogleEmbeddingsEndpoint(StrEnum):
    """Endpoints for Google Embeddings API."""

    EMBED_CONTENT = "/v1beta/models/{model_id}:embedContent"
    BATCH_EMBED_CONTENTS = "/v1beta/models/{model_id}:batchEmbedContents"


BASE_URL = "https://generativelanguage.googleapis.com"
