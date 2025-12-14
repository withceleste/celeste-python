"""Cohere provider configuration for text generation."""

# HTTP Configuration
BASE_URL = "https://api.cohere.com"
ENDPOINT = "/v2/chat"
STREAM_ENDPOINT = ENDPOINT

# Authentication
AUTH_HEADER_NAME = "Authorization"
AUTH_HEADER_PREFIX = "Bearer "
CLIENT_NAME_HEADER = "X-Client-Name"
