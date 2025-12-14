"""OpenAI provider configuration for video generation."""

# HTTP Configuration
BASE_URL = "https://api.openai.com"
ENDPOINT = "/v1/videos"
CONTENT_ENDPOINT_SUFFIX = "/content"

# Authentication
AUTH_HEADER_NAME = "Authorization"
AUTH_HEADER_PREFIX = "Bearer "

# Polling Configuration
MAX_POLLS = 60
POLL_INTERVAL = 5  # seconds

# Status Constants
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
