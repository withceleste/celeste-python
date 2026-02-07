"""Configuration for Google Embeddings API."""

from enum import StrEnum


class GoogleEmbeddingsEndpoint(StrEnum):
    """Endpoints for Google Embeddings API."""

    EMBED_CONTENT = "/v1beta/models/{model_id}:embedContent"
    BATCH_EMBED_CONTENTS = "/v1beta/models/{model_id}:batchEmbedContents"


class VertexEmbeddingsEndpoint(StrEnum):
    """Endpoints for Embeddings on Vertex AI."""

    EMBED_CONTENT = "/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model_id}:predict"
    BATCH_EMBED_CONTENTS = "/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model_id}:predict"


BASE_URL = "https://generativelanguage.googleapis.com"
