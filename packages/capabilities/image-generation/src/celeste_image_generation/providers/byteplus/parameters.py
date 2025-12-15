"""BytePlus Images parameter mappers for image generation."""

from typing import Any

from celeste_byteplus.images.parameters import (
    SizeMapper as _SizeMapper,
)
from celeste_byteplus.images.parameters import (
    WatermarkMapper as _WatermarkMapper,
)

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste_image_generation.parameters import ImageGenerationParameter


class AspectRatioMapper(_SizeMapper):
    name = ImageGenerationParameter.ASPECT_RATIO


class QualityMapper(_SizeMapper):
    """Map quality to BytePlus size field with conflict resolution."""

    name = ImageGenerationParameter.QUALITY

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform quality into provider request.

        Skips if size is already set by aspect_ratio (conflict resolution).
        """
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        # Skip if size already set by aspect_ratio parameter
        if "size" in request:
            return request

        return super().map(request, validated_value, model)


class WatermarkMapper(_WatermarkMapper):
    name = ImageGenerationParameter.WATERMARK


BYTEPLUS_PARAMETER_MAPPERS: list[ParameterMapper] = [
    AspectRatioMapper(),
    QualityMapper(),
    WatermarkMapper(),
]

__all__ = ["BYTEPLUS_PARAMETER_MAPPERS"]
