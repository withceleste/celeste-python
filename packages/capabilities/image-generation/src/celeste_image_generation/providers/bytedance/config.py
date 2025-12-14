"""ByteDance provider configuration for image generation."""

# HTTP Configuration
BASE_URL = "https://ark.ap-southeast.bytepluses.com/api/v3"
ENDPOINT = "/images/generations"
STREAM_ENDPOINT = "/responses"

# Authentication
AUTH_HEADER_NAME = "Authorization"
AUTH_HEADER_PREFIX = "Bearer "
