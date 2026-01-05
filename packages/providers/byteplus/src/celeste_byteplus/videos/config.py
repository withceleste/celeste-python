"""Configuration for BytePlus Videos API."""

from enum import StrEnum


class BytePlusVideosEndpoint(StrEnum):
    """Endpoints for BytePlus Videos API."""

    CREATE_VIDEO = "/api/v3/contents/generations/tasks"
    GET_VIDEO_STATUS = "/api/v3/contents/generations/tasks/{task_id}"


BASE_URL = "https://ark.ap-southeast.bytepluses.com"

# Polling Configuration
POLLING_INTERVAL = 5  # seconds
POLLING_TIMEOUT = 300  # 5 minutes

# Status Constants
STATUS_SUCCEEDED = "succeeded"
STATUS_FAILED = "failed"
STATUS_CANCELED = "canceled"
