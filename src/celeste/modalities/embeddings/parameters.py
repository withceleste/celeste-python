"""Parameters for embeddings modality."""

from enum import StrEnum
from typing import Annotated

from pydantic import Field

from celeste.parameters import Parameters


class EmbeddingsParameter(StrEnum):
    """Parameter names for embeddings."""

    DIMENSIONS = "dimensions"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"


class EmbeddingsParameters(Parameters, total=False):
    """Parameters for embeddings operations."""

    dimensions: Annotated[int | None, Field(description="Embedding vector length.")]


__all__ = [
    "EmbeddingsParameter",
    "EmbeddingsParameters",
]
