"""OpenAI provider configuration for image generation."""

# HTTP Configuration
BASE_URL = "https://api.openai.com"
ENDPOINT = "/v1/images/generations"
STREAM_ENDPOINT = ENDPOINT  # Same endpoint, streaming enabled via request parameter

# Authentication
AUTH_HEADER_NAME = "Authorization"
AUTH_HEADER_PREFIX = "Bearer "
