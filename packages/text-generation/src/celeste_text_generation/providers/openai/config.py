"""OpenAI provider configuration."""

# HTTP Configuration
BASE_URL = "https://api.openai.com"
ENDPOINT = "/v1/responses"
STREAM_ENDPOINT = ENDPOINT

# Authentication
AUTH_HEADER_NAME = "Authorization"
AUTH_HEADER_PREFIX = "Bearer "
