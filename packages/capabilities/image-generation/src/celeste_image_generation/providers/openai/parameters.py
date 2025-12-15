"""OpenAI Images parameter mappers for image generation."""

from celeste_openai.images.parameters import (
    PartialImagesMapper as _PartialImagesMapper,
)
from celeste_openai.images.parameters import (
    QualityMapper as _QualityMapper,
)
from celeste_openai.images.parameters import (
    SizeMapper as _SizeMapper,
)

from celeste.parameters import ParameterMapper
from celeste_image_generation.parameters import ImageGenerationParameter


class AspectRatioMapper(_SizeMapper):
    name = ImageGenerationParameter.ASPECT_RATIO


class PartialImagesMapper(_PartialImagesMapper):
    name = ImageGenerationParameter.PARTIAL_IMAGES


class QualityMapper(_QualityMapper):
    name = ImageGenerationParameter.QUALITY


OPENAI_PARAMETER_MAPPERS: list[ParameterMapper] = [
    AspectRatioMapper(),
    PartialImagesMapper(),
    QualityMapper(),
]

__all__ = ["OPENAI_PARAMETER_MAPPERS"]
