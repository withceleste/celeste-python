"""BFL parameter mappers for videos."""

from celeste.parameters import ParameterMapper
from celeste.providers.bfl.flux.parameters import (
    AspectRatioMapper as _AspectRatioMapper,
)
from celeste.providers.bfl.flux.parameters import (
    DurationMapper as _DurationMapper,
)
from celeste.providers.bfl.flux.parameters import (
    FirstFrameMapper as _FirstFrameMapper,
)
from celeste.providers.bfl.flux.parameters import (
    LastFrameMapper as _LastFrameMapper,
)
from celeste.providers.bfl.flux.parameters import (
    ResolutionMapper as _ResolutionMapper,
)
from celeste.types import VideoContent

from ...parameters import VideoParameter


class AspectRatioMapper(_AspectRatioMapper[VideoContent]):
    """Map aspect_ratio to BFL's aspect_ratio parameter."""

    name = VideoParameter.ASPECT_RATIO


class ResolutionMapper(_ResolutionMapper[VideoContent]):
    """Map resolution to BFL's resolution parameter."""

    name = VideoParameter.RESOLUTION


class DurationMapper(_DurationMapper):
    """Map duration to BFL's duration parameter."""

    name = VideoParameter.DURATION


class FirstFrameMapper(_FirstFrameMapper):
    """Map first_frame to BFL's keyframes parameter."""

    name = VideoParameter.FIRST_FRAME


class LastFrameMapper(_LastFrameMapper):
    """Map last_frame to BFL's keyframes parameter."""

    name = VideoParameter.LAST_FRAME


BFL_PARAMETER_MAPPERS: list[ParameterMapper[VideoContent]] = [
    AspectRatioMapper(),
    ResolutionMapper(),
    DurationMapper(),
    FirstFrameMapper(),
    LastFrameMapper(),
]

__all__ = ["BFL_PARAMETER_MAPPERS"]
