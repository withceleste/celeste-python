"""Configuration for the BFL Videos API."""

from enum import StrEnum


class BFLVideosEndpoint(StrEnum):
    """Endpoints for the BFL Videos API."""

    CREATE_VIDEO = "/v1/flux-3-video"


POLLING_INTERVAL = 2.0
POLLING_TIMEOUT = 300.0

__all__ = ["POLLING_INTERVAL", "POLLING_TIMEOUT", "BFLVideosEndpoint"]
