"""Configuration for Gradium Text-to-Speech API."""

from enum import StrEnum


class GradiumTextToSpeechEndpoint(StrEnum):
    """Endpoints for Text-to-Speech API."""

    CREATE_SPEECH = "/speech/tts"


BASE_URL = "wss://eu.api.gradium.ai/api"
