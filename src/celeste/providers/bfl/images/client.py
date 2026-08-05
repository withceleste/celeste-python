"""BFL Images API client mixin."""

from celeste.providers.bfl.client import BFLAsyncClient

from . import config


class BFLImagesClient(BFLAsyncClient):
    """Mixin for BFL Images API operations."""

    _default_endpoint = config.BFLImagesEndpoint.CREATE_IMAGE
    _operation_label = "image generation"
    _polling_interval = config.POLLING_INTERVAL
    _polling_timeout = config.POLLING_TIMEOUT


__all__ = ["BFLImagesClient"]
