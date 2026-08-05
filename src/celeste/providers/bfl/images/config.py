"""Configuration for BFL Images API."""

from enum import StrEnum


class BFLImagesEndpoint(StrEnum):
    """Endpoints for BFL Images API."""

    CREATE_IMAGE = "/v1/{model_id}"


# Polling Configuration
POLLING_INTERVAL = 0.5  # seconds between polling attempts
POLLING_TIMEOUT = 120.0  # 2 minutes timeout
