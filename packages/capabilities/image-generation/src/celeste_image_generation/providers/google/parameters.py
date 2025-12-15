"""Google Gemini and Imagen parameter mappers for image generation."""

from celeste.parameters import ParameterMapper

from .gemini_parameters import GEMINI_PARAMETER_MAPPERS
from .imagen_parameters import IMAGEN_PARAMETER_MAPPERS

GOOGLE_PARAMETER_MAPPERS: list[ParameterMapper] = (
    GEMINI_PARAMETER_MAPPERS + IMAGEN_PARAMETER_MAPPERS
)

__all__ = ["GOOGLE_PARAMETER_MAPPERS"]
