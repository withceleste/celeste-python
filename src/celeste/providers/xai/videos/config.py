"""Configuration for xAI Videos API."""

from enum import StrEnum


class XAIVideosEndpoint(StrEnum):
    """Endpoints for xAI Videos API."""

    CREATE_VIDEO = "/v1/videos/generations"
    CREATE_EDIT = "/v1/videos/edits"


BASE_URL = "https://api.x.ai"

# Polling Configuration
MAX_POLLS = 60
POLL_INTERVAL = 5  # seconds

# Status Constants
STATUS_FAILED = "failed"
