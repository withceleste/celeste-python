"""OpenAI images client."""

from typing import Any, Unpack

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
    ImageOutput,
)
from ...parameters import ImageParameters
from ...streaming import ImagesStream
from .parameters import OPENAI_PARAMETER_MAPPERS


class OpenAIImagesStream(_OpenAIImagesStream, ImagesStream):
    """OpenAI streaming for images modality."""

    def _aggregate_content(self, chunks: list[ImageChunk]) -> ImageArtifact:
        """Aggregate image content from chunks."""
        return chunks[-1].content


class OpenAIImagesClient(OpenAIImagesMixin, ImagesClient):
    """OpenAI images client."""

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

    async def generate(
        self,
        prompt: str,
        **parameters: Unpack[ImageParameters],
    ) -> ImageOutput:
        """Generate images from prompt."""
        inputs = ImageInput(prompt=prompt)
        return await self._predict(
            inputs,
            endpoint=config.OpenAIImagesEndpoint.CREATE_IMAGE,
            **parameters,
        )

    async def edit(
        self,
        image: ImageArtifact,
        prompt: str,
        **parameters: Unpack[ImageParameters],
    ) -> ImageOutput:
        """Edit an image with text instructions."""
        inputs = ImageInput(image=image, prompt=prompt)
        return await self._predict(
            inputs,
            endpoint=config.OpenAIImagesEndpoint.CREATE_EDIT,
            **parameters,
        )

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> ImageArtifact:
        """Parse content from response."""
        data = super()._parse_content(response_data)
        image_data = data[0]

        b64_json = image_data.get("b64_json")
        if b64_json:
            return ImageArtifact(data=b64_json)

        url = image_data.get("url")
        if url:
            return ImageArtifact(url=url)

        msg = "No image URL or base64 data in response"
        raise ValueError(msg)

    def _stream_class(self) -> type[ImagesStream]:
        """Return the Stream class for this provider."""
        return OpenAIImagesStream


__all__ = ["OpenAIImagesClient", "OpenAIImagesStream"]
