"""Google provider configuration for text generation."""

# HTTP Configuration
BASE_URL = "https://generativelanguage.googleapis.com"
ENDPOINT = "/v1beta/models/{model_id}:generateContent"
STREAM_ENDPOINT = "/v1beta/models/{model_id}:streamGenerateContent?alt=sse"

# Authentication
AUTH_HEADER_NAME = "x-goog-api-key"
AUTH_HEADER_PREFIX = ""  # Empty string for plain key
