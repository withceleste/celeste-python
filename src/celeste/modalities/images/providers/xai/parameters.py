"""xAI parameter mappers for images."""

from celeste.parameters import ParameterMapper
from celeste.providers.xai.images.parameters import (
    AspectRatioMapper as _AspectRatioMapper,
)
from celeste.providers.xai.images.parameters import (
    NumImagesMapper as _NumImagesMapper,
)
from celeste.providers.xai.images.parameters import (
    ResolutionMapper as _ResolutionMapper,
)
from celeste.providers.xai.images.parameters import (
    ResponseFormatMapper as _ResponseFormatMapper,
)
from celeste.types import ImageContent

from ...parameters import ImageParameter


class AspectRatioMapper(_AspectRatioMapper):
    """Map aspect_ratio to xAI's aspect_ratio parameter."""

    name = ImageParameter.ASPECT_RATIO


class NumImagesMapper(_NumImagesMapper):
    """Map num_images to xAI's n parameter."""

    name = ImageParameter.NUM_IMAGES


class OutputFormatMapper(_ResponseFormatMapper):
    """Map output_format to xAI's response_format parameter."""

    name = ImageParameter.OUTPUT_FORMAT


class QualityMapper(_ResolutionMapper):
    """Map quality to xAI's resolution parameter."""

    name = ImageParameter.QUALITY


XAI_PARAMETER_MAPPERS: list[ParameterMapper[ImageContent]] = [
    AspectRatioMapper(),
    NumImagesMapper(),
    OutputFormatMapper(),
    QualityMapper(),
]

__all__ = ["XAI_PARAMETER_MAPPERS"]
