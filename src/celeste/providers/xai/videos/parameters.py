"""xAI Videos API parameter mappers."""

from typing import Any

from celeste.models import Model
from celeste.parameters import FieldMapper, ParameterMapper
from celeste.types import VideoContent
from celeste.utils import build_data_url


class DurationMapper(FieldMapper[VideoContent]):
    """Map duration to xAI duration field."""

    field = "duration"


class AspectRatioMapper(FieldMapper[VideoContent]):
    """Map aspect_ratio to xAI aspect_ratio field."""

    field = "aspect_ratio"


class ResolutionMapper(FieldMapper[VideoContent]):
    """Map resolution to xAI resolution field."""

    field = "resolution"


class FirstFrameMapper(ParameterMapper[VideoContent]):
    """Map an image-to-video first frame to xAI's image field."""

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Transform first_frame into the provider request."""
        if self._warn_if_unsupported(value, model):
            return request

        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request
        request["image"] = {"url": build_data_url(validated_value)}
        return request


__all__ = [
    "AspectRatioMapper",
    "DurationMapper",
    "FirstFrameMapper",
    "ResolutionMapper",
]
