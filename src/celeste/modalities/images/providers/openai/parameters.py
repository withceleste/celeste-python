"""OpenAI parameter mappers for images."""

from celeste.parameters import ParameterMapper
from celeste.providers.openai.images.parameters import (
    PartialImagesMapper as _PartialImagesMapper,
)
from celeste.providers.openai.images.parameters import (
    QualityMapper as _QualityMapper,
)
from celeste.providers.openai.images.parameters import (
    SizeMapper as _SizeMapper,
)

from ...parameters import ImageParameter


class AspectRatioMapper(_SizeMapper):
    """Map aspect_ratio to OpenAI's size parameter."""

    name = ImageParameter.ASPECT_RATIO


class PartialImagesMapper(_PartialImagesMapper):
    """Map partial_images to OpenAI's partial_images parameter."""

    name = ImageParameter.PARTIAL_IMAGES


class QualityMapper(_QualityMapper):
    """Map quality to OpenAI's quality parameter."""

    name = ImageParameter.QUALITY


OPENAI_PARAMETER_MAPPERS: list[ParameterMapper] = [
    AspectRatioMapper(),
    PartialImagesMapper(),
    QualityMapper(),
]

__all__ = ["OPENAI_PARAMETER_MAPPERS"]
