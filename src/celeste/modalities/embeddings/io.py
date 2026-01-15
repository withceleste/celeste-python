"""IO types for embeddings modality."""

from pydantic import Field

from celeste.io import Chunk, FinishReason, Input, Output, Usage
from celeste.types import EmbeddingsContent


class EmbeddingsInput(Input):
    """Input for embeddings operations."""

    text: str | list[str]


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
