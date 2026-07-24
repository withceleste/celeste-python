"""Topaz Labs images client."""

from typing import Any

from celeste.artifacts import ImageArtifact
from celeste.parameters import ParameterMapper
from celeste.providers.topazlabs.image.client import (
    TopazLabsImageClient as TopazLabsImageMixin,
)
from celeste.types import ImageContent

from ...client import ImagesClient
from ...io import ImageFinishReason, ImageInput
from .parameters import TOPAZLABS_PARAMETER_MAPPERS

# Capability sentinel only; submit path is resolved per model id in the wire mixin.
_UPSCALE_SUPPORTED = "model-routed"


class TopazLabsImagesClient(TopazLabsImageMixin, ImagesClient):
    """Topaz Labs images client (upscale only)."""

    _upscale_endpoint = _UPSCALE_SUPPORTED

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[ImageContent]]:
        return TOPAZLABS_PARAMETER_MAPPERS

    def _init_request(self, inputs: ImageInput) -> dict[str, Any]:
        """Build request with the input image for multipart upload."""
        return {"image": inputs.image}

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> ImageArtifact:
        """Parse content from response."""
        download_url = super()._parse_content(response_data)
        return ImageArtifact(url=download_url)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> ImageFinishReason:
        """Parse finish reason from response."""
        finish_reason = super()._parse_finish_reason(response_data)
        return ImageFinishReason(reason=finish_reason.reason)


__all__ = ["TopazLabsImagesClient"]
