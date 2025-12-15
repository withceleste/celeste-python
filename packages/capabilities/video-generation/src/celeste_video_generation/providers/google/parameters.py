"""Google Veo parameter mappers for video generation."""

from celeste_google.veo.parameters import (
    AspectRatioMapper as _AspectRatioMapper,
)
from celeste_google.veo.parameters import (
    DurationSecondsMapper as _DurationSecondsMapper,
)
from celeste_google.veo.parameters import (
    FirstFrameMapper as _FirstFrameMapper,
)
from celeste_google.veo.parameters import (
    LastFrameMapper as _LastFrameMapper,
)
from celeste_google.veo.parameters import (
    ReferenceImagesMapper as _ReferenceImagesMapper,
)
from celeste_google.veo.parameters import (
    ResolutionMapper as _ResolutionMapper,
)

from celeste.parameters import ParameterMapper
from celeste_video_generation.parameters import VideoGenerationParameter


class AspectRatioMapper(_AspectRatioMapper):
    name = VideoGenerationParameter.ASPECT_RATIO


class ResolutionMapper(_ResolutionMapper):
    name = VideoGenerationParameter.RESOLUTION


class DurationMapper(_DurationSecondsMapper):
    name = VideoGenerationParameter.DURATION


class ReferenceImagesMapper(_ReferenceImagesMapper):
    name = VideoGenerationParameter.REFERENCE_IMAGES


class FirstFrameMapper(_FirstFrameMapper):
    name = VideoGenerationParameter.FIRST_FRAME


class LastFrameMapper(_LastFrameMapper):
    name = VideoGenerationParameter.LAST_FRAME


GOOGLE_PARAMETER_MAPPERS: list[ParameterMapper] = [
    AspectRatioMapper(),
    ResolutionMapper(),
    DurationMapper(),
    ReferenceImagesMapper(),
    FirstFrameMapper(),
    LastFrameMapper(),
]

__all__ = ["GOOGLE_PARAMETER_MAPPERS"]
