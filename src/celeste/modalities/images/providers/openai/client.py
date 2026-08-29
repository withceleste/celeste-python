"""OpenAI images client."""

from typing import Any

from celeste.artifacts import ImageArtifact
from celeste.parameters import ParameterMapper
from celeste.providers.openai.images import config
from celeste.providers.openai.images.client import (
    OpenAIImagesClient as OpenAIImagesMixin,
)
from celeste.providers.openai.images.streaming import (
    OpenAIImagesStream as _OpenAIImagesStream,
)
from celeste.types import ImageContent

from ...client import ImagesClient
from ...io import (
    ImageChunk,
    ImageInput,
)
from ...streaming import ImagesStream
from .parameters import OPENAI_PARAMETER_MAPPERS


class OpenAIImagesStream(_OpenAIImagesStream, ImagesStream):
    """OpenAI streaming for images modality."""

    def _aggregate_content(self, chunks: list[ImageChunk]) -> ImageArtifact:
        """Aggregate image content from chunks."""
        return chunks[-1].content


class OpenAIImagesClient(OpenAIImagesMixin, ImagesClient):
    """OpenAI images client."""

    _generate_endpoint = config.OpenAIImagesEndpoint.CREATE_IMAGE
    _edit_endpoint = config.OpenAIImagesEndpoint.CREATE_EDIT

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[ImageContent]]:
        return OPENAI_PARAMETER_MAPPERS

    def _init_request(self, inputs: ImageInput) -> dict[str, Any]:
        """Initialize request, keeping ImageArtifact for multipart handling."""
        request: dict[str, Any] = {"prompt": inputs.prompt}
        if inputs.image is not None:
            # Keep as ImageArtifact - _make_multipart_request handles encoding
            request["image"] = inputs.image
        return request

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> ImageContent:
        """Parse content from response."""
        data = super()._parse_content(response_data)
        images: list[ImageArtifact] = []

        for image_data in data:
            if b64_json := image_data.get("b64_json"):
                images.append(ImageArtifact(data=b64_json))
            elif url := image_data.get("url"):
                images.append(ImageArtifact(url=url))
            else:
                msg = "No image URL or base64 data in response"
                raise ValueError(msg)

        return images[0] if len(images) == 1 else images

    def _stream_class(self) -> type[ImagesStream]:
        """Return the Stream class for this provider."""
        return OpenAIImagesStream


__all__ = ["OpenAIImagesClient", "OpenAIImagesStream"]
