"""Configuration for DeepSeek Chat API."""

from enum import StrEnum


class DeepSeekChatEndpoint(StrEnum):
    """Endpoints for DeepSeek Chat API."""

    CREATE_CHAT = "/v1/chat/completions"
    LIST_MODELS = "/models"


class VertexDeepSeekEndpoint(StrEnum):
    """Endpoints for DeepSeek on Vertex AI (OpenAI-compatible)."""

    CREATE_CHAT = "/v1/projects/{project_id}/locations/{location}/endpoints/openapi/chat/completions"


BASE_URL = "https://api.deepseek.com"
