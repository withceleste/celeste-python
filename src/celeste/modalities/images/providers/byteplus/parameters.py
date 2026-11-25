"""BytePlus parameter mappers for images modality."""

from celeste.parameters import ParameterMapper
from celeste.providers.byteplus.images.parameters import (
    BackgroundMapper as _BackgroundMapper,
    ImageMapper as _ImageMapper,
    OutputFormatMapper as _OutputFormatMapper,
    SizeMapper as _SizeMapper,
    WatermarkMapper as _WatermarkMapper,
)
from celeste.types import ImageContent

from ...parameters import ImageParameter


class AspectRatioMapper(_SizeMapper):
    name = ImageParameter.ASPECT_RATIO


class QualityMapper(_SizeMapper):
    """Map quality to BytePlus size field."""

    name = ImageParameter.QUALITY


class ReferenceImagesMapper(_ImageMapper):
    name = ImageParameter.REFERENCE_IMAGES


class WatermarkMapper(_WatermarkMapper):
    name = ImageParameter.WATERMARK


class OutputFormatMapper(_OutputFormatMapper):
    name = ImageParameter.OUTPUT_FORMAT


class BackgroundMapper(_BackgroundMapper):
    name = ImageParameter.BACKGROUND


BYTEPLUS_PARAMETER_MAPPERS: list[ParameterMapper[ImageContent]] = [
    AspectRatioMapper(),
    QualityMapper(),
    ReferenceImagesMapper(),
    WatermarkMapper(),
    OutputFormatMapper(),
    BackgroundMapper(),
]

__all__ = ["BYTEPLUS_PARAMETER_MAPPERS"]
