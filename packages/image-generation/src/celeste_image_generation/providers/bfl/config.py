"""BFL (Black Forest Labs) provider configuration for image generation."""

# HTTP Configuration
BASE_URL = "https://api.bfl.ai"
ENDPOINT = "/v1/{model_id}"

# Authentication
AUTH_HEADER_NAME = "x-key"
AUTH_HEADER_PREFIX = ""  # Direct API key, no prefix

# Polling Configuration
POLLING_INTERVAL = 0.5  # seconds between polling attempts
POLLING_TIMEOUT = 120.0  # 2 minutes for image generation
