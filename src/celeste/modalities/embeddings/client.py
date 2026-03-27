"""Embeddings modality client."""

from typing import Any, Unpack

from asgiref.sync import async_to_sync

from celeste.client import ModalityClient
from celeste.core import Modality
from celeste.types import EmbeddingsContent, ImageContent, VideoContent

from .io import (
    EmbeddingsChunk,
    EmbeddingsFinishReason,
    EmbeddingsInput,
    EmbeddingsOutput,
    EmbeddingsUsage,
)
from .parameters import EmbeddingsParameters


class EmbeddingsClient(
    ModalityClient[
        EmbeddingsInput,
        EmbeddingsOutput,
        EmbeddingsParameters,
        EmbeddingsContent,
        EmbeddingsChunk,
    ]
):
    """Base embeddings client. Providers implement operation methods."""

    modality: Modality = Modality.EMBEDDINGS
    _usage_class = EmbeddingsUsage
    _finish_reason_class = EmbeddingsFinishReason

    @classmethod
    def _output_class(cls) -> type[EmbeddingsOutput]:
        """Return the Output class for embeddings modality."""
        return EmbeddingsOutput

    async def embed(
        self,
        text: str | list[str] | None = None,
        *,
        images: ImageContent | None = None,
        videos: VideoContent | None = None,
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[EmbeddingsParameters],
    ) -> EmbeddingsOutput:
        """Generate embeddings from text, images, or video.

        Args:
            text: Text to embed. Single string or list of strings.
            images: Image(s) to embed. Single ImageArtifact or list.
            videos: Video(s) to embed. Single VideoArtifact or list.
            extra_body: Additional provider-specific fields to merge into request.
            extra_headers: Additional HTTP headers to include in the request.
            **parameters: Embedding parameters (e.g., dimensions).

        Returns:
            EmbeddingsOutput with content as EmbeddingsContent:
            - Single vector for single inputs (str, ImageArtifact, VideoArtifact)
            - List of vectors for batch inputs (list[str], list[ImageArtifact], etc.)
        """
        inputs = EmbeddingsInput(text=text, images=images, videos=videos)
        output = await self._predict(
            inputs, extra_body=extra_body, extra_headers=extra_headers, **parameters
        )

        # Unwrap single-item results from batch format
        is_batch = (
            isinstance(text, list)
            or isinstance(images, list)
            or isinstance(videos, list)
        )
        if (
            not is_batch
            and isinstance(output.content, list)
            and output.content
            and isinstance(output.content[0], list)
        ):
            output.content = output.content[0]

        return output

    @property
    def sync(self) -> "EmbeddingsSyncNamespace":
        """Sync namespace for embeddings operations."""
        return EmbeddingsSyncNamespace(self)


class EmbeddingsSyncNamespace:
    """Sync namespace for embeddings operations."""

    def __init__(self, client: EmbeddingsClient) -> None:
        self._client = client

    def embed(
        self,
        text: str | list[str] | None = None,
        *,
        images: ImageContent | None = None,
        videos: VideoContent | None = None,
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[EmbeddingsParameters],
    ) -> EmbeddingsOutput:
        """Blocking embeddings generation."""
        return async_to_sync(self._client.embed)(
            text,
            images=images,
            videos=videos,
            extra_body=extra_body,
            extra_headers=extra_headers,
            **parameters,
        )


__all__ = [
    "EmbeddingsClient",
    "EmbeddingsSyncNamespace",
]
