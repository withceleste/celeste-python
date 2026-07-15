"""xAI images client."""

from typing import Any

from celeste.artifacts import ImageArtifact
from celeste.parameters import ParameterMapper
from celeste.providers.xai.images import config
from celeste.providers.xai.images.client import XAIImagesClient as XAIImagesMixin
from celeste.types import ImageContent
from celeste.utils import build_data_url

from ...client import ImagesClient
from ...io import (
    ImageInput,
)
from .parameters import XAI_PARAMETER_MAPPERS


class XAIImagesClient(XAIImagesMixin, ImagesClient):
    """xAI images client."""

    _generate_endpoint = config.XAIImagesEndpoint.CREATE_IMAGE
    _edit_endpoint = config.XAIImagesEndpoint.CREATE_EDIT

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[ImageContent]]:
        return XAI_PARAMETER_MAPPERS

    def _init_request(self, inputs: ImageInput) -> dict[str, Any]:
        """Initialize request from inputs."""
        request: dict[str, Any] = {"prompt": inputs.prompt}
        if inputs.image is not None:
            request["image"] = {"url": build_data_url(inputs.image)}
        return request

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> ImageArtifact:
        """Parse content from response."""
        data = super()._parse_content(response_data)
        image_data = data[0]

        # xAI returns either b64_json or url
        b64_json = image_data.get("b64_json")
        if b64_json:
            return ImageArtifact(data=b64_json)

        url = image_data.get("url")
        if url:
            return ImageArtifact(url=url)

        msg = "No image URL or base64 data in response"
        raise ValueError(msg)


__all__ = ["XAIImagesClient"]
