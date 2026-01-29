"""xAI parameter mappers for videos."""

from celeste.parameters import ParameterMapper
from celeste.providers.xai.videos.parameters import (
    AspectRatioMapper as _AspectRatioMapper,
)
from celeste.providers.xai.videos.parameters import (
    DurationMapper as _DurationMapper,
)
from celeste.providers.xai.videos.parameters import (
    ResolutionMapper as _ResolutionMapper,
)

from ...parameters import VideoParameter


class DurationMapper(_DurationMapper):
    """Map duration to xAI's duration parameter."""

    name = VideoParameter.DURATION


class AspectRatioMapper(_AspectRatioMapper):
    """Map aspect_ratio to xAI's aspect_ratio parameter."""

    name = VideoParameter.ASPECT_RATIO


class ResolutionMapper(_ResolutionMapper):
    """Map resolution to xAI's resolution parameter."""

    name = VideoParameter.RESOLUTION


XAI_PARAMETER_MAPPERS: list[ParameterMapper] = [
    DurationMapper(),
    AspectRatioMapper(),
    ResolutionMapper(),
]

__all__ = ["XAI_PARAMETER_MAPPERS"]
