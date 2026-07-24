"""Segmentation modality client."""

from typing import Any, ClassVar, Unpack

from asgiref.sync import async_to_sync

from celeste.artifacts import ImageArtifact
from celeste.client import ModalityClient
from celeste.core import Modality
from celeste.types import SegmentationContent

from .io import (
    SegmentationChunk,
    SegmentationFinishReason,
    SegmentationInput,
    SegmentationOutput,
    SegmentationUsage,
)
from .parameters import SegmentationParameters


class SegmentationClient(
    ModalityClient[
        SegmentationInput,
        SegmentationOutput,
        SegmentationParameters,
        SegmentationContent,
        SegmentationChunk,
    ]
):
    """Base segmentation client with segment operation."""

    modality: Modality = Modality.SEGMENTATION
    _usage_class = SegmentationUsage
    _finish_reason_class = SegmentationFinishReason

    _segment_endpoint: ClassVar[str | None] = None

    @classmethod
    def _output_class(cls) -> type[SegmentationOutput]:
        """Return the Output class for segmentation modality."""
        return SegmentationOutput

    async def segment(
        self,
        image: ImageArtifact,
        prompt: str | None = None,
        *,
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[SegmentationParameters],
    ) -> SegmentationOutput:
        """Segment an image with an optional text concept and visual prompts."""
        inputs = SegmentationInput(image=image, prompt=prompt)
        return await self._predict(
            inputs,
            endpoint=self._segment_endpoint,
            extra_body=extra_body,
            extra_headers=extra_headers,
            **parameters,
        )

    @property
    def sync(self) -> "SegmentationSyncNamespace":
        """Sync namespace for segmentation operations."""
        return SegmentationSyncNamespace(self)


class SegmentationSyncNamespace:
    """Sync namespace for segmentation operations."""

    def __init__(self, client: SegmentationClient) -> None:
        self._client = client

    def segment(
        self,
        image: ImageArtifact,
        prompt: str | None = None,
        *,
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[SegmentationParameters],
    ) -> SegmentationOutput:
        """Blocking image segmentation."""
        return async_to_sync(self._client.segment)(
            image,
            prompt,
            extra_body=extra_body,
            extra_headers=extra_headers,
            **parameters,
        )


__all__ = [
    "SegmentationClient",
    "SegmentationSyncNamespace",
]
