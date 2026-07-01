"""Configuration for OpenAI Videos API."""

import os
from enum import StrEnum


class OpenAIVideosEndpoint(StrEnum):
    """Endpoints for OpenAI Videos API."""

    CREATE_VIDEO = "/v1/videos"


# Support custom base URL via environment variable (for OpenAI-compatible APIs)
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com")
CONTENT_ENDPOINT_SUFFIX = "/content"

# Polling Configuration
MAX_POLLS = 60
POLL_INTERVAL = 5  # seconds

# Status Constants
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
