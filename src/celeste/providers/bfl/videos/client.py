"""BFL Videos API client mixin."""

from celeste.providers.bfl.client import BFLAsyncClient

from . import config


class BFLVideosClient(BFLAsyncClient):
    """Mixin for BFL Videos API operations."""

    _default_endpoint = config.BFLVideosEndpoint.CREATE_VIDEO
    _operation_label = "video generation"
    _polling_interval = config.POLLING_INTERVAL
    _polling_timeout = config.POLLING_TIMEOUT


__all__ = ["BFLVideosClient"]
