"""OpenAI parameter mappers for images."""

from celeste.parameters import ParameterMapper
from celeste.providers.openai.images.parameters import (
    BackgroundMapper as _BackgroundMapper,
)
from celeste.providers.openai.images.parameters import (
    ModerationMapper as _ModerationMapper,
)
from celeste.providers.openai.images.parameters import (
    NumImagesMapper as _NumImagesMapper,
)
from celeste.providers.openai.images.parameters import (
    OutputCompressionMapper as _OutputCompressionMapper,
)
from celeste.providers.openai.images.parameters import (
    OutputFormatMapper as _OutputFormatMapper,
)
from celeste.providers.openai.images.parameters import (
    PartialImagesMapper as _PartialImagesMapper,
)
from celeste.providers.openai.images.parameters import (
    QualityMapper as _QualityMapper,
)
from celeste.providers.openai.images.parameters import (
    SizeMapper as _SizeMapper,
)
from celeste.types import ImageContent

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


class NumImagesMapper(_NumImagesMapper):
    """Map num_images to OpenAI's n parameter."""

    name = ImageParameter.NUM_IMAGES


class OutputFormatMapper(_OutputFormatMapper):
    """Map output_format to OpenAI's output_format parameter."""

    name = ImageParameter.OUTPUT_FORMAT


class BackgroundMapper(_BackgroundMapper):
    """Map background to OpenAI's background parameter."""

    name = ImageParameter.BACKGROUND


class ModerationMapper(_ModerationMapper):
    """Map moderation to OpenAI's moderation parameter."""

    name = ImageParameter.MODERATION


class OutputCompressionMapper(_OutputCompressionMapper):
    """Map output_compression to OpenAI's output_compression parameter."""

    name = ImageParameter.OUTPUT_COMPRESSION


OPENAI_PARAMETER_MAPPERS: list[ParameterMapper[ImageContent]] = [
    AspectRatioMapper(),
    PartialImagesMapper(),
    QualityMapper(),
    NumImagesMapper(),
    OutputFormatMapper(),
    BackgroundMapper(),
    ModerationMapper(),
    OutputCompressionMapper(),
]

__all__ = ["OPENAI_PARAMETER_MAPPERS"]
