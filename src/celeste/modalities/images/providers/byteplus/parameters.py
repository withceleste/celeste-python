"""BytePlus parameter mappers for images modality."""

from celeste.parameters import ParameterMapper
from celeste.providers.byteplus.images.parameters import (
    SizeMapper as _SizeMapper,
)
from celeste.providers.byteplus.images.parameters import (
    WatermarkMapper as _WatermarkMapper,
)

from ...parameters import ImageParameter


class AspectRatioMapper(_SizeMapper):
    name = ImageParameter.ASPECT_RATIO


class QualityMapper(_SizeMapper):
    """Map quality to BytePlus size field with conflict resolution."""

    name = ImageParameter.QUALITY


class WatermarkMapper(_WatermarkMapper):
    name = ImageParameter.WATERMARK


BYTEPLUS_PARAMETER_MAPPERS: list[ParameterMapper] = [
    AspectRatioMapper(),
    QualityMapper(),
    WatermarkMapper(),
]

__all__ = ["BYTEPLUS_PARAMETER_MAPPERS"]
