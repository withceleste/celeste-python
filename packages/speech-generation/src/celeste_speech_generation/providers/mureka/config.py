"""Mureka provider configuration for speech generation."""

# HTTP Configuration
BASE_URL = "https://api.mureka.ai"

# Endpoints
TTS_GENERATE_ENDPOINT = "/v1/tts/generate"
PODCAST_GENERATE_ENDPOINT = "/v1/tts/podcast"

# Authentication
AUTH_HEADER_NAME = "Authorization"
AUTH_HEADER_PREFIX = "Bearer "

__all__ = [
    "AUTH_HEADER_NAME",
    "AUTH_HEADER_PREFIX",
    "BASE_URL",
    "PODCAST_GENERATE_ENDPOINT",
    "TTS_GENERATE_ENDPOINT",
]
