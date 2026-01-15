"""Configuration for Google Interactions API."""

from enum import StrEnum


class GoogleInteractionsEndpoint(StrEnum):
    """Endpoints for Google Interactions API."""

    CREATE_INTERACTION = "/v1beta/interactions"
    GET_INTERACTION = "/v1beta/interactions/{interaction_id}"
    STREAM_INTERACTION = "/v1beta/interactions?alt=sse"


BASE_URL = "https://generativelanguage.googleapis.com"

# Polling Configuration (for background mode)
POLLING_INTERVAL = 5  # seconds
POLLING_TIMEOUT = 300  # 5 minutes

# Status Constants
STATUS_COMPLETED = "completed"
STATUS_IN_PROGRESS = "in_progress"
STATUS_REQUIRES_ACTION = "requires_action"
STATUS_FAILED = "failed"
STATUS_CANCELLED = "cancelled"
