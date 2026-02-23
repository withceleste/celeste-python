"""Images streaming primitives."""

from abc import abstractmethod
from typing import Any

from celeste.artifacts import ImageArtifact
from celeste.streaming import Stream

from .io import ImageChunk, ImageFinishReason, ImageOutput, ImageUsage
from .parameters import ImageParameters


class ImagesStream(Stream[ImageOutput, ImageParameters, ImageChunk]):
    """Streaming for images modality."""

    _usage_class = ImageUsage
    _finish_reason_class = ImageFinishReason
    _chunk_class = ImageChunk
    _output_class = ImageOutput
    _empty_content = ImageArtifact(data=b"")

    def _wrap_chunk_content(self, raw_content: Any) -> ImageArtifact:  # noqa: ANN401
        """Wrap raw content (base64 string) into ImageArtifact."""
        return ImageArtifact(data=raw_content)

    @abstractmethod
    def _aggregate_content(self, chunks: list[ImageChunk]) -> ImageArtifact:
        """Aggregate content from chunks into raw content (modality-specific)."""
        ...


__all__ = ["ImagesStream"]
