"""Images modality client."""

from typing import Any, Unpack

from asgiref.sync import async_to_sync

from celeste.artifacts import ImageArtifact
from celeste.client import ModalityClient
from celeste.core import Modality
from celeste.types import ImageContent

from .io import ImageInput, ImageOutput
from .parameters import ImageParameters
from .streaming import ImagesStream


class ImagesClient(
    ModalityClient[ImageInput, ImageOutput, ImageParameters, ImageContent]
):
    """Base images client. Providers implement generate/edit methods."""

    modality: Modality = Modality.IMAGES

    @classmethod
    def _output_class(cls) -> type[ImageOutput]:
        """Return the Output class for images modality."""
        return ImageOutput

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
        **parameters: Unpack[ImageParameters],
    ) -> ImagesStream:
        """Stream image generation."""
        inputs = ImageInput(prompt=prompt)
        return self._client._stream(
            inputs,
            stream_class=self._client._stream_class(),
            extra_body=extra_body,
            **parameters,
        )

    def edit(
        self,
        image: ImageArtifact,
        prompt: str,
        *,
        extra_body: dict[str, Any] | None = None,
        **parameters: Unpack[ImageParameters],
    ) -> ImagesStream:
        """Stream image editing."""
        inputs = ImageInput(prompt=prompt, image=image)
        return self._client._stream(
            inputs,
            stream_class=self._client._stream_class(),
            extra_body=extra_body,
            **parameters,
        )


class ImagesSyncNamespace:
    """Sync namespace for images operations.

    Provides `client.sync.generate()` and `client.sync.edit()`.
    """

    def __init__(self, client: ImagesClient) -> None:
        self._client = client

    def generate(
        self,
        prompt: str,
        *,
        extra_body: dict[str, Any] | None = None,
        **parameters: Unpack[ImageParameters],
    ) -> ImageOutput:
        """Blocking image generation.

        Usage:
            result = client.sync.generate("A sunset over mountains")
            result.content.show()
        """
        inputs = ImageInput(prompt=prompt)
        return async_to_sync(self._client._predict)(
            inputs, extra_body=extra_body, **parameters
        )

    def edit(
        self,
        image: ImageArtifact,
        prompt: str,
        *,
        extra_body: dict[str, Any] | None = None,
        **parameters: Unpack[ImageParameters],
    ) -> ImageOutput:
        """Blocking image edit.

        Usage:
            result = client.sync.edit(image, "Add a rainbow")
            result.content.show()
        """
        inputs = ImageInput(prompt=prompt, image=image)
        return async_to_sync(self._client._predict)(
            inputs, extra_body=extra_body, **parameters
        )

    @property
    def stream(self) -> "ImagesSyncStreamNamespace":
        """Sync streaming namespace."""
        return ImagesSyncStreamNamespace(self._client)


class ImagesSyncStreamNamespace:
    """Sync streaming namespace - returns Stream instance with sync iteration support."""

    def __init__(self, client: ImagesClient) -> None:
        self._client = client

    def generate(
        self,
        prompt: str,
        *,
        extra_body: dict[str, Any] | None = None,
        **parameters: Unpack[ImageParameters],
    ) -> ImagesStream:
        """Sync streaming image generation.

        Returns Stream instance that supports both async and sync iteration.

        Usage:
            stream = client.sync.stream.generate("A sunset over mountains")
            for chunk in stream:  # Sync iteration (bridges async internally)
                print(chunk.content)
            print(stream.output.usage)
        """
        # Return same stream as async version - __iter__/__next__ handle sync iteration
        return self._client.stream.generate(prompt, extra_body=extra_body, **parameters)

    def edit(
        self,
        image: ImageArtifact,
        prompt: str,
        *,
        extra_body: dict[str, Any] | None = None,
        **parameters: Unpack[ImageParameters],
    ) -> ImagesStream:
        """Sync streaming image editing.

        Returns Stream instance that supports both async and sync iteration.

        Usage:
            stream = client.sync.stream.edit(image, "Add a rainbow")
            for chunk in stream:
                print(chunk.content)
            print(stream.output.usage)
        """
        return self._client.stream.edit(
            image, prompt, extra_body=extra_body, **parameters
        )


__all__ = [
    "ImagesClient",
    "ImagesStreamNamespace",
    "ImagesSyncNamespace",
    "ImagesSyncStreamNamespace",
]
