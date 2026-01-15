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

from ...parameters import VideoParameter

# Resolution to height mapping
_RESOLUTION_HEIGHT: dict[str, int] = {
    "720p": 720,
    "1080p": 1080,
    "4k": 2160,
}

# Aspect ratio to (width_ratio, height_ratio) mapping
_ASPECT_RATIOS: dict[str, tuple[int, int]] = {
    "16:9": (16, 9),
    "9:16": (9, 16),
    "1:1": (1, 1),
    "4:3": (4, 3),
    "3:4": (3, 4),
}


def _compute_size(aspect_ratio: str, resolution: str) -> str:
    """Compute OpenAI size from aspect ratio and resolution.

    Args:
        aspect_ratio: Aspect ratio like "16:9" or "9:16".
        resolution: Resolution like "720p" or "1080p".

    Returns:
        Size string like "1280x720".
    """
    height = _RESOLUTION_HEIGHT.get(resolution, 720)
    width_ratio, height_ratio = _ASPECT_RATIOS.get(aspect_ratio, (16, 9))

    # Compute width from height and aspect ratio
    width = int(height * width_ratio / height_ratio)

    return f"{width}x{height}"


class AspectRatioMapper(ParameterMapper):
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
        size = _compute_size(aspect_ratio, str(validated_value))

        # Delegate to provider's SizeMapper
        return super().map(request, size, model)


class DurationMapper(_SecondsMapper):
    """Map duration to OpenAI's seconds parameter."""

    name = VideoParameter.DURATION


OPENAI_PARAMETER_MAPPERS: list[ParameterMapper] = [
    AspectRatioMapper(),
    ResolutionMapper(),
    DurationMapper(),
]

__all__ = ["OPENAI_PARAMETER_MAPPERS"]
