"""Google provider configuration for image generation."""

# HTTP Configuration
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
IMAGEN_ENDPOINT = "/{model_id}:predict"
GEMINI_ENDPOINT = "/{model_id}:generateContent"

# Authentication
AUTH_HEADER_NAME = "x-goog-api-key"
AUTH_HEADER_PREFIX = ""  # Direct API key, no prefix
