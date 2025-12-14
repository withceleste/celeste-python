"""ByteDance provider configuration for video generation."""

# HTTP Configuration
BASE_URL = "https://ark.ap-southeast.bytepluses.com/api/v3"
ENDPOINT = "/contents/generations/tasks"
STATUS_ENDPOINT_TEMPLATE = "/contents/generations/tasks/{task_id}"

# Authentication
AUTH_HEADER_NAME = "Authorization"
AUTH_HEADER_PREFIX = "Bearer "

# Polling Configuration
DEFAULT_POLLING_INTERVAL = 5  # seconds
MAX_POLLING_TIMEOUT = 300  # 5 minutes

# Status Constants
STATUS_SUCCEEDED = "succeeded"
STATUS_FAILED = "failed"
STATUS_CANCELED = "canceled"
