"""OpenAI parameter mappers for videos.

OpenAI Videos API uses a single `size` parameter (e.g., "1280x720") instead of
separate aspect_ratio and resolution parameters. This module provides unification
logic to transform Celeste's unified parameters to OpenAI's format.

Mapping:
- aspect_ratio="16:9" + resolution="720p" → size="1280x720"
- aspect_ratio="9:16" + resolution="720p" → size="720x1280"
"""

from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.providers.openai.videos.parameters import (
    SecondsMapper as _SecondsMapper,
)
from celeste.providers.openai.videos.parameters import (
    SizeMapper as _SizeMapper,
)
from celeste.types import VideoContent

from ...parameters import VideoParameter

# (aspect_ratio, resolution) → documented OpenAI size; catalogs permit only these combos
_SIZES: dict[tuple[str, str], str] = {
    ("16:9", "720p"): "1280x720",
    ("9:16", "720p"): "720x1280",
    ("16:9", "1080p"): "1920x1080",
    ("9:16", "1080p"): "1080x1920",
}


class AspectRatioMapper(ParameterMapper[VideoContent]):
    """Store aspect_ratio for later combination with resolution."""

    name = VideoParameter.ASPECT_RATIO

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Store aspect_ratio for ResolutionMapper to use."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["_aspect_ratio"] = validated_value
        return request


class ResolutionMapper(_SizeMapper):
    """Combine resolution with stored aspect_ratio to compute size."""

    name = VideoParameter.RESOLUTION

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Compute size from resolution and stored aspect_ratio."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        aspect_ratio = request.pop("_aspect_ratio", "16:9")
        size = _SIZES.get((aspect_ratio, str(validated_value)), "1280x720")

        # Delegate to provider's SizeMapper
        return super().map(request, size, model)


class DurationMapper(_SecondsMapper):
    """Map duration to OpenAI's seconds parameter."""

    name = VideoParameter.DURATION


OPENAI_PARAMETER_MAPPERS: list[ParameterMapper[VideoContent]] = [
    AspectRatioMapper(),
    ResolutionMapper(),
    DurationMapper(),
]

__all__ = ["OPENAI_PARAMETER_MAPPERS"]
