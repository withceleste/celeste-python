"""Embeddings modality client."""

from typing import Any, Unpack

from asgiref.sync import async_to_sync

from celeste.client import ModalityClient
from celeste.core import Modality
from celeste.types import EmbeddingsContent

from .io import EmbeddingsInput, EmbeddingsOutput
from .parameters import EmbeddingsParameters


class EmbeddingsClient(
    ModalityClient[
        EmbeddingsInput, EmbeddingsOutput, EmbeddingsParameters, EmbeddingsContent
    ]
):
    """Base embeddings client. Providers implement operation methods."""

    modality: Modality = Modality.EMBEDDINGS

    @classmethod
    def _output_class(cls) -> type[EmbeddingsOutput]:
        """Return the Output class for embeddings modality."""
        return EmbeddingsOutput

    async def embed(
        self,
        text: str | list[str],
        *,
        extra_body: dict[str, Any] | None = None,
        **parameters: Unpack[EmbeddingsParameters],
    ) -> EmbeddingsOutput:
        """Generate embeddings from text.

        Args:
            text: Text to embed. Single string or list of strings.
            extra_body: Additional provider-specific fields to merge into request.
            **parameters: Embedding parameters (e.g., dimensions).

        Returns:
            EmbeddingsOutput with content as:
            - list[float] if text was a string
            - list[list[float]] if text was a list
        """
        inputs = EmbeddingsInput(text=text)
        output = await self._predict(inputs, extra_body=extra_body, **parameters)

        # If single text input, unwrap from batch format to single embedding
        if (
            isinstance(text, str)
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
        text: str | list[str],
        *,
        extra_body: dict[str, Any] | None = None,
        **parameters: Unpack[EmbeddingsParameters],
    ) -> EmbeddingsOutput:
        """Blocking embeddings generation."""
        return async_to_sync(self._client.embed)(
            text, extra_body=extra_body, **parameters
        )


__all__ = [
    "EmbeddingsClient",
    "EmbeddingsSyncNamespace",
]
