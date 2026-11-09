"""OpenAI Images API parameter mappers."""

from typing import Any

from celeste.models import Model
from celeste.parameters import FieldMapper, ParameterMapper
from celeste.types import ImageContent
from celeste.utils import build_data_url


class SizeMapper(FieldMapper[ImageContent]):
    """Map size to OpenAI size field."""

    field = "size"


class PartialImagesMapper(FieldMapper[ImageContent]):
    """Map partial_images to OpenAI partial_images field."""

    field = "partial_images"


class QualityMapper(FieldMapper[ImageContent]):
    """Map quality to OpenAI quality field."""

    field = "quality"


class BackgroundMapper(FieldMapper[ImageContent]):
    """Map background to OpenAI background field."""

    field = "background"


class OutputFormatMapper(FieldMapper[ImageContent]):
    """Map output_format to OpenAI output_format field."""

    field = "output_format"


class StyleMapper(FieldMapper[ImageContent]):
    """Map style to OpenAI style field."""

    field = "style"


class ModerationMapper(FieldMapper[ImageContent]):
    """Map moderation to OpenAI moderation field."""

    field = "moderation"


class OutputCompressionMapper(FieldMapper[ImageContent]):
    """Map output_compression to OpenAI output_compression field."""

    field = "output_compression"


class NumImagesMapper(FieldMapper[ImageContent]):
    """Map num_images to OpenAI n field."""

    field = "n"


class ImagesMapper(ParameterMapper[ImageContent]):
    """Map images to OpenAI images field, after the edit image if present."""

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Transform images into provider request."""
        validated_value = self._validate_value(value, model)
        if not validated_value:
            return request

        request.setdefault("images", []).extend(
            {"image_url": build_data_url(image)} for image in validated_value
        )
        return request


class MaskMapper(ParameterMapper[ImageContent]):
    """Map mask to OpenAI mask field."""

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Transform mask into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["mask"] = {"image_url": build_data_url(validated_value)}
        return request


__all__ = [
    "BackgroundMapper",
    "ImagesMapper",
    "MaskMapper",
    "ModerationMapper",
    "NumImagesMapper",
    "OutputCompressionMapper",
    "OutputFormatMapper",
    "PartialImagesMapper",
    "QualityMapper",
    "SizeMapper",
    "StyleMapper",
]
