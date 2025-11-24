"""XAI provider configuration for text generation."""

# HTTP Configuration
BASE_URL = "https://api.x.ai/v1"
ENDPOINT = "/chat/completions"
STREAM_ENDPOINT = ENDPOINT

# Authentication
AUTH_HEADER_NAME = "Authorization"
AUTH_HEADER_PREFIX = "Bearer "
