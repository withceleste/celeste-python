"""Configuration for Google Live API."""

from enum import StrEnum


class GoogleLiveEndpoint(StrEnum):
    """Endpoints for Google Live API."""

    BIDI_GENERATE_CONTENT = (
        "/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent"
    )


class VertexLiveEndpoint(StrEnum):
    """Endpoints for Live on Vertex AI."""

    BIDI_GENERATE_CONTENT = (
        "/ws/google.cloud.aiplatform.v1.LlmBidiService/BidiGenerateContent"
    )


BASE_URL = "wss://generativelanguage.googleapis.com"
