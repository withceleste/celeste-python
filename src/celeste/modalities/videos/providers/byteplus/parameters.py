"""BytePlus parameter mappers for videos."""

from celeste.parameters import ParameterMapper
from celeste.providers.byteplus.videos.parameters import (
    AspectRatioMapper as _AspectRatioMapper,
    DurationMapper as _DurationMapper,
    FirstFrameMapper as _FirstFrameMapper,
    LastFrameMapper as _LastFrameMapper,
    ReferenceImagesMapper as _ReferenceImagesMapper,
    ResolutionMapper as _ResolutionMapper,
)
from celeste.types import VideoContent

from ...parameters import VideoParameter


class AspectRatioMapper(_AspectRatioMapper):
    """Map aspect_ratio to BytePlus's --ratio prompt flag."""

    name = VideoParameter.ASPECT_RATIO


class ResolutionMapper(_ResolutionMapper):
    """Map resolution to BytePlus's --resolution prompt flag."""

    name = VideoParameter.RESOLUTION


class DurationMapper(_DurationMapper):
    """Map duration to BytePlus's --duration prompt flag."""

    name = VideoParameter.DURATION


class ReferenceImagesMapper(_ReferenceImagesMapper):
    """Map reference_images to BytePlus content array."""

    name = VideoParameter.REFERENCE_IMAGES


class FirstFrameMapper(_FirstFrameMapper):
    """Map first_frame to BytePlus content array."""

    name = VideoParameter.FIRST_FRAME


class LastFrameMapper(_LastFrameMapper):
    """Map last_frame to BytePlus content array."""

    name = VideoParameter.LAST_FRAME


BYTEPLUS_PARAMETER_MAPPERS: list[ParameterMapper[VideoContent]] = [
    AspectRatioMapper(),
    ResolutionMapper(),
    DurationMapper(),
    ReferenceImagesMapper(),
    FirstFrameMapper(),
    LastFrameMapper(),
]

__all__ = ["BYTEPLUS_PARAMETER_MAPPERS"]
