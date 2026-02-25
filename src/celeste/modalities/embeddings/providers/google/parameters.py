"""Google parameter mappers for embeddings."""

from celeste.parameters import ParameterMapper
from celeste.providers.google.embeddings.parameters import (
    OutputDimensionalityMapper as _OutputDimensionalityMapper,
)
from celeste.types import EmbeddingsContent

from ...parameters import EmbeddingsParameter


class DimensionsMapper(_OutputDimensionalityMapper):
    """Map dimensions to Google's outputDimensionality parameter."""

    name = EmbeddingsParameter.DIMENSIONS


GOOGLE_PARAMETER_MAPPERS: list[ParameterMapper[EmbeddingsContent]] = [
    DimensionsMapper(),
]

__all__ = ["GOOGLE_PARAMETER_MAPPERS"]
