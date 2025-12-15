"""Google Gemini parameter mappers for image generation."""

from celeste_google.generate_content.parameters import (
    AspectRatioMapper as _AspectRatioMapper,
)
from celeste_google.generate_content.parameters import (
    ImageSizeMapper as _ImageSizeMapper,
)
from celeste_google.generate_content.parameters import (
    MediaContentMapper as _MediaContentMapper,
)

from celeste.parameters import ParameterMapper
from celeste_image_generation.parameters import ImageGenerationParameter


class AspectRatioMapper(_AspectRatioMapper):
    name = ImageGenerationParameter.ASPECT_RATIO


class QualityMapper(_ImageSizeMapper):
    name = ImageGenerationParameter.QUALITY


class ReferenceImagesMapper(_MediaContentMapper):
    name = ImageGenerationParameter.REFERENCE_IMAGES


GEMINI_PARAMETER_MAPPERS: list[ParameterMapper] = [
    AspectRatioMapper(),
    QualityMapper(),
    ReferenceImagesMapper(),
]

__all__ = ["GEMINI_PARAMETER_MAPPERS"]
