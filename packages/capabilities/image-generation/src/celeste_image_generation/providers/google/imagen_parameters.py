"""Google Imagen parameter mappers for image generation."""

from celeste_google.imagen.parameters import (
    AspectRatioMapper as _AspectRatioMapper,
)
from celeste_google.imagen.parameters import (
    ImageSizeMapper as _ImageSizeMapper,
)
from celeste_google.imagen.parameters import (
    SampleCountMapper as _SampleCountMapper,
)

from celeste.parameters import ParameterMapper
from celeste_image_generation.parameters import ImageGenerationParameter


class AspectRatioMapper(_AspectRatioMapper):
    name = ImageGenerationParameter.ASPECT_RATIO


class QualityMapper(_ImageSizeMapper):
    name = ImageGenerationParameter.QUALITY


class NumImagesMapper(_SampleCountMapper):
    name = ImageGenerationParameter.NUM_IMAGES


IMAGEN_PARAMETER_MAPPERS: list[ParameterMapper] = [
    AspectRatioMapper(),
    QualityMapper(),
    NumImagesMapper(),
]

__all__ = ["IMAGEN_PARAMETER_MAPPERS"]
