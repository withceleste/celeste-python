"""Images modality client."""

from typing import Any, ClassVar, Unpack

from asgiref.sync import async_to_sync

from celeste.artifacts import ImageArtifact
from celeste.client import ModalityClient
from celeste.core import Modality
from celeste.types import ImageContent

from .io import ImageChunk, ImageFinishReason, ImageInput, ImageOutput, ImageUsage
from .parameters import ImageParameters
from .streaming import ImagesStream


class ImagesClient(
    ModalityClient[ImageInput, ImageOutput, ImageParameters, ImageContent, ImageChunk]
):
    """Base images client with generate/edit/upscale operations."""

    modality: Modality = Modality.IMAGES
    _usage_class = ImageUsage
    _finish_reason_class = ImageFinishReason

    _generate_endpoint: ClassVar[str | None] = None
    _edit_endpoint: ClassVar[str | None] = None
    _upscale_endpoint: ClassVar[str | None] = None

    @classmethod
    def _output_class(cls) -> type[ImageOutput]:
        """Return the Output class for images modality."""
        return ImageOutput

    async def generate(
        self,
        prompt: str,
        *,
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[ImageParameters],
    ) -> ImageOutput:
        """Generate images from prompt."""
        inputs = ImageInput(prompt=prompt)
        return await self._predict(
            inputs,
            endpoint=self._generate_endpoint,
            extra_body=extra_body,
            extra_headers=extra_headers,
            **parameters,
        )

    async def edit(
        self,
        image: ImageArtifact,
        prompt: str,
        *,
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[ImageParameters],
    ) -> ImageOutput:
        """Edit an image with text instructions."""
        if self._edit_endpoint is None:
            msg = f"Model {self.model.id} does not support image editing"
            raise NotImplementedError(msg)
        inputs = ImageInput(prompt=prompt, image=image)
        return await self._predict(
            inputs,
            endpoint=self._edit_endpoint,
            extra_body=extra_body,
            extra_headers=extra_headers,
            **parameters,
        )

    async def upscale(
        self,
        image: ImageArtifact,
        *,
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[ImageParameters],
    ) -> ImageOutput:
        """Upscale an image."""
        if self._upscale_endpoint is None:
            msg = f"Model {self.model.id} does not support image upscaling"
            raise NotImplementedError(msg)
        inputs = ImageInput(image=image)
        return await self._predict(
            inputs,
            endpoint=self._upscale_endpoint,
            extra_body=extra_body,
            extra_headers=extra_headers,
            **parameters,
        )

    @property
    def stream(self) -> "ImagesStreamNamespace":
        """Streaming namespace for images operations."""
        return ImagesStreamNamespace(self)

    @property
    def sync(self) -> "ImagesSyncNamespace":
        """Sync namespace for images operations."""
        return ImagesSyncNamespace(self)


class ImagesStreamNamespace:
    """Streaming namespace for images operations.

    Provides `client.stream.generate()` and `client.stream.edit()`.
    """

    def __init__(self, client: ImagesClient) -> None:
        self._client = client

    def generate(
        self,
        prompt: str,
        *,
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[ImageParameters],
    ) -> ImagesStream:
        """Stream image generation."""
        inputs = ImageInput(prompt=prompt)
        return self._client._stream(
            inputs,
            stream_class=self._client._stream_class(),
            extra_body=extra_body,
            extra_headers=extra_headers,
            **parameters,
        )

    def edit(
        self,
        image: ImageArtifact,
        prompt: str,
        *,
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[ImageParameters],
    ) -> ImagesStream:
        """Stream image editing."""
        if self._client._edit_endpoint is None:
            msg = f"Model {self._client.model.id} does not support image editing"
            raise NotImplementedError(msg)
        inputs = ImageInput(prompt=prompt, image=image)
        return self._client._stream(
            inputs,
            stream_class=self._client._stream_class(),
            extra_body=extra_body,
            extra_headers=extra_headers,
            **parameters,
        )


class ImagesSyncNamespace:
    """Sync namespace for images operations.

    Provides `client.sync.generate()`, `client.sync.edit()`, and `client.sync.upscale()`.
    """

    def __init__(self, client: ImagesClient) -> None:
        self._client = client
        self.generate = async_to_sync(client.generate)
        self.edit = async_to_sync(client.edit)
        self.upscale = async_to_sync(client.upscale)

    @property
    def stream(self) -> "ImagesSyncStreamNamespace":
        """Sync streaming namespace."""
        return ImagesSyncStreamNamespace(self._client)


ImagesSyncStreamNamespace = ImagesStreamNamespace


__all__ = [
    "ImagesClient",
    "ImagesStreamNamespace",
    "ImagesSyncNamespace",
    "ImagesSyncStreamNamespace",
]
