"""IO types for embeddings modality."""

from pydantic import Field, model_validator

from celeste.io import Chunk, FinishReason, Input, Output, Usage
from celeste.types import EmbeddingsContent, ImageContent, VideoContent


class EmbeddingsInput(Input):
    """Input for embeddings operations."""

    text: str | list[str] | None = None
    images: ImageContent | None = None
    videos: VideoContent | None = None

    @model_validator(mode="after")
    def _validate_inputs(self) -> "EmbeddingsInput":
        if self.text is None and self.images is None and self.videos is None:
            msg = "At least one of text, images, or videos must be provided"
            raise ValueError(msg)
        if isinstance(self.text, list) and (
            self.images is not None or self.videos is not None
        ):
            msg = "Batch text (list[str]) cannot be combined with images or videos"
            raise ValueError(msg)
        return self


class EmbeddingsFinishReason(FinishReason):
    """Embeddings finish reason (for consistency)."""

    reason: str | None = None
    message: str | None = None


class EmbeddingsUsage(Usage):
    """Embeddings usage metrics."""

    input_tokens: int | None = None
    total_tokens: int | None = None


class EmbeddingsOutput(Output[EmbeddingsContent]):
    """Output from embeddings operations."""

    usage: EmbeddingsUsage = Field(default_factory=EmbeddingsUsage)
    finish_reason: EmbeddingsFinishReason | None = None


class EmbeddingsChunk(Chunk[list[float]]):
    """Chunk for embeddings streaming (for consistency, not used in practice)."""

    finish_reason: EmbeddingsFinishReason | None = None
    usage: EmbeddingsUsage | None = None


__all__ = [
    "EmbeddingsChunk",
    "EmbeddingsFinishReason",
    "EmbeddingsInput",
    "EmbeddingsOutput",
    "EmbeddingsUsage",
]
