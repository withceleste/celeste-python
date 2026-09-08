"""IO types for embeddings modality."""

from pydantic import Field, model_validator

from celeste.io import Chunk, FinishReason, Input, Output, Usage
from celeste.types import AudioContent, EmbeddingsContent, ImageContent, VideoContent


class EmbeddingsInput(Input):
    """Input for embeddings operations."""

    text: str | list[str] | None = None
    images: ImageContent | None = None
    videos: VideoContent | None = None
    audio: AudioContent | None = None

    @model_validator(mode="after")
    def _validate_inputs(self) -> "EmbeddingsInput":
        inputs = {
            "text": self.text,
            "images": self.images,
            "videos": self.videos,
            "audio": self.audio,
        }
        provided = {name: value for name, value in inputs.items() if value is not None}
        if not provided:
            msg = "At least one of text, images, videos, or audio must be provided"
            raise ValueError(msg)
        for name, value in provided.items():
            if isinstance(value, list) and len(provided) > 1:
                raise ValueError(f"Batch {name} cannot be combined with other inputs")
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
