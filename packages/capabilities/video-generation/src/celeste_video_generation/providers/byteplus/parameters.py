"""BytePlus parameter mappers for video generation."""

from celeste_byteplus.videos.parameters import (
    DurationMapper as _DurationMapper,
)
from celeste_byteplus.videos.parameters import (
    FirstFrameMapper as _FirstFrameMapper,
)
from celeste_byteplus.videos.parameters import (
    LastFrameMapper as _LastFrameMapper,
)
from celeste_byteplus.videos.parameters import (
    ReferenceImagesMapper as _ReferenceImagesMapper,
)
from celeste_byteplus.videos.parameters import (
    ResolutionMapper as _ResolutionMapper,
)

from celeste.parameters import ParameterMapper
from celeste_video_generation.parameters import VideoGenerationParameter


class DurationMapper(_DurationMapper):
    name = VideoGenerationParameter.DURATION


class ResolutionMapper(_ResolutionMapper):
    name = VideoGenerationParameter.RESOLUTION


class ReferenceImagesMapper(_ReferenceImagesMapper):
    name = VideoGenerationParameter.REFERENCE_IMAGES


class FirstFrameMapper(_FirstFrameMapper):
    name = VideoGenerationParameter.FIRST_FRAME


class LastFrameMapper(_LastFrameMapper):
    name = VideoGenerationParameter.LAST_FRAME


BYTEPLUS_PARAMETER_MAPPERS: list[ParameterMapper] = [
    DurationMapper(),
    ResolutionMapper(),
    ReferenceImagesMapper(),
    FirstFrameMapper(),
    LastFrameMapper(),
]

__all__ = ["BYTEPLUS_PARAMETER_MAPPERS"]
