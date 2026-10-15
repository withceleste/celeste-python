"""BytePlus Images API parameter mappers."""

from typing import Any

from celeste.models import Model
from celeste.parameters import FieldMapper, ParameterMapper
from celeste.types import ImageContent
from celeste.utils import build_data_url


class ImageMapper(ParameterMapper[ImageContent]):
    """Map images to BytePlus image field, after the edit image if present."""

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Transform images into provider request."""
        validated_value = self._validate_value(value, model)
        if not validated_value:
            return request

        images = [request["image"]] if "image" in request else []
        images.extend(build_data_url(image) for image in validated_value)
        request["image"] = images
        return request


class SizeMapper(FieldMapper[ImageContent]):
    """Map size to BytePlus size field."""

    field = "size"


class WatermarkMapper(FieldMapper[ImageContent]):
    """Map watermark to BytePlus watermark field."""

    field = "watermark"


__all__ = ["ImageMapper", "SizeMapper", "WatermarkMapper"]
