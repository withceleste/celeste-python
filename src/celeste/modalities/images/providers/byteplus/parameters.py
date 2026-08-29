"""BytePlus parameter mappers for images modality."""

from typing import Any

from celeste.constraints import ImagesConstraint
from celeste.exceptions import ConstraintViolationError
from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.providers.byteplus.images.parameters import (
    BackgroundMapper as _BackgroundMapper,
)
from celeste.providers.byteplus.images.parameters import (
    OutputFormatMapper as _OutputFormatMapper,
)
from celeste.providers.byteplus.images.parameters import (
    SizeMapper as _SizeMapper,
)
from celeste.providers.byteplus.images.parameters import (
    WatermarkMapper as _WatermarkMapper,
)
from celeste.types import ImageContent
from celeste.utils import build_data_url

from ...parameters import ImageParameter


class AspectRatioMapper(_SizeMapper):
    name = ImageParameter.ASPECT_RATIO


class QualityMapper(_SizeMapper):
    """Map quality to BytePlus size field."""

    name = ImageParameter.QUALITY


class WatermarkMapper(_WatermarkMapper):
    name = ImageParameter.WATERMARK


class OutputFormatMapper(_OutputFormatMapper):
    name = ImageParameter.OUTPUT_FORMAT


class BackgroundMapper(_BackgroundMapper):
    name = ImageParameter.BACKGROUND


class ReferenceImagesMapper(ParameterMapper[ImageContent]):
    name = ImageParameter.REFERENCE_IMAGES

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Append ordered reference images to the primary edit image, when present."""
        references = self._validate_value(value, model)
        if not references:
            return request

        current = request.get("image")
        constraint = model.parameter_constraints.get(self.name)
        current_count = (
            0 if current is None else (1 if isinstance(current, str) else len(current))
        )
        if (
            isinstance(constraint, ImagesConstraint)
            and constraint.max_count is not None
            and current_count + len(references) > constraint.max_count
        ):
            msg = f"BytePlus accepts at most {constraint.max_count} total input images"
            raise ConstraintViolationError(msg)

        images = (
            []
            if current is None
            else ([current] if isinstance(current, str) else list(current))
        )
        images.extend(build_data_url(image) for image in references)
        request["image"] = images[0] if len(images) == 1 else images
        return request


BYTEPLUS_PARAMETER_MAPPERS: list[ParameterMapper[ImageContent]] = [
    AspectRatioMapper(),
    QualityMapper(),
    WatermarkMapper(),
    OutputFormatMapper(),
    BackgroundMapper(),
    ReferenceImagesMapper(),
]

__all__ = ["BYTEPLUS_PARAMETER_MAPPERS"]
