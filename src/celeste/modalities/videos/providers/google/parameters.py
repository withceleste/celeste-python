"""Google parameter mappers for videos."""

from celeste.parameters import ParameterMapper
from celeste.providers.google.veo.parameters import (
    AspectRatioMapper as _AspectRatioMapper,
)
from celeste.providers.google.veo.parameters import (
    DurationSecondsMapper as _DurationSecondsMapper,
)
from celeste.providers.google.veo.parameters import (
    FirstFrameMapper as _FirstFrameMapper,
)
from celeste.providers.google.veo.parameters import (
    LastFrameMapper as _LastFrameMapper,
)
from celeste.providers.google.veo.parameters import (
    ReferenceImagesMapper as _ReferenceImagesMapper,
)
from celeste.providers.google.veo.parameters import (
    ResolutionMapper as _ResolutionMapper,
)

from ...parameters import VideoParameter


class AspectRatioMapper(_AspectRatioMapper):
    """Map aspect_ratio to Google Veo's aspectRatio parameter."""

    name = VideoParameter.ASPECT_RATIO


class ResolutionMapper(_ResolutionMapper):
    """Map resolution to Google Veo's resolution parameter."""

    name = VideoParameter.RESOLUTION


class DurationMapper(_DurationSecondsMapper):
    """Map duration to Google Veo's durationSeconds parameter."""

    name = VideoParameter.DURATION


class ReferenceImagesMapper(_ReferenceImagesMapper):
    """Map reference_images to Google Veo's referenceImages parameter."""

    name = VideoParameter.REFERENCE_IMAGES


class FirstFrameMapper(_FirstFrameMapper):
    """Map first_frame to Google Veo's image parameter."""

    name = VideoParameter.FIRST_FRAME


class LastFrameMapper(_LastFrameMapper):
    """Map last_frame to Google Veo's lastFrame parameter."""

    name = VideoParameter.LAST_FRAME


GOOGLE_PARAMETER_MAPPERS: list[ParameterMapper] = [
    AspectRatioMapper(),
    ResolutionMapper(),
    DurationMapper(),
    ReferenceImagesMapper(),
    FirstFrameMapper(),
    LastFrameMapper(),
]

__all__ = ["GOOGLE_PARAMETER_MAPPERS"]
