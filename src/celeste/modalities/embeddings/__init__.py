"""Celeste Embeddings modality."""

from .client import EmbeddingsClient
from .io import (
    EmbeddingsChunk,
    EmbeddingsFinishReason,
    EmbeddingsInput,
    EmbeddingsOutput,
    EmbeddingsUsage,
)
from .parameters import EmbeddingsParameter, EmbeddingsParameters

__all__ = [
    "EmbeddingsChunk",
    "EmbeddingsClient",
    "EmbeddingsFinishReason",
    "EmbeddingsInput",
    "EmbeddingsOutput",
    "EmbeddingsParameter",
    "EmbeddingsParameters",
    "EmbeddingsUsage",
]
