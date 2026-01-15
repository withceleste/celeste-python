"""Google parameter mappers for embeddings."""

from celeste.parameters import ParameterMapper
from celeste.providers.google.embeddings.parameters import (
    OutputDimensionalityMapper as _OutputDimensionalityMapper,
)

from ...parameters import EmbeddingsParameter


class DimensionsMapper(_OutputDimensionalityMapper):
    """Map dimensions to Google's outputDimensionality parameter."""

    name = EmbeddingsParameter.DIMENSIONS


GOOGLE_PARAMETER_MAPPERS: list[ParameterMapper] = [
    DimensionsMapper(),
]

__all__ = ["GOOGLE_PARAMETER_MAPPERS"]
