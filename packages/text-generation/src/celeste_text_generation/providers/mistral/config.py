"""Mistral provider configuration for text generation."""

# HTTP Configuration
BASE_URL = "https://api.mistral.ai"
ENDPOINT = "/v1/chat/completions"
STREAM_ENDPOINT = ENDPOINT  # Same endpoint

# Authentication
AUTH_HEADER_NAME = "Authorization"
AUTH_HEADER_PREFIX = "Bearer "
