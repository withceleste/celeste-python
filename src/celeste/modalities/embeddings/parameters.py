"""Parameters for embeddings modality."""

from enum import StrEnum

from celeste.parameters import Parameters


class EmbeddingsParameter(StrEnum):
    """Parameter names for embeddings."""

    DIMENSIONS = "dimensions"


class EmbeddingsParameters(Parameters):
    """Parameters for embeddings operations."""

    dimensions: int | None


__all__ = [
    "EmbeddingsParameter",
    "EmbeddingsParameters",
]
