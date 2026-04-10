"""Parameters for embeddings modality."""

from enum import StrEnum

from celeste.parameters import Parameters


class EmbeddingsParameter(StrEnum):
    """Parameter names for embeddings."""

    DIMENSIONS = "dimensions"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"


class EmbeddingsParameters(Parameters, total=False):
    """Parameters for embeddings operations."""

    dimensions: int | None


__all__ = [
    "EmbeddingsParameter",
    "EmbeddingsParameters",
]
