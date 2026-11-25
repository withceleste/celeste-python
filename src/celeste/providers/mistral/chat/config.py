"""Configuration for Mistral Chat API."""

from enum import StrEnum


class MistralChatEndpoint(StrEnum):
    """Endpoints for Mistral Chat API."""

    CREATE_CHAT_COMPLETION = "/v1/chat/completions"


class VertexChatEndpoint(StrEnum):
    """Endpoints for Mistral on Vertex AI."""

    CREATE_CHAT = "/v1/projects/{project_id}/locations/{location}/publishers/mistralai/models/{model_id}:rawPredict"
    STREAM_CHAT = "/v1/projects/{project_id}/locations/{location}/publishers/mistralai/models/{model_id}:streamRawPredict"


BASE_URL = "https://api.mistral.ai"
