"""BFL parameter mappers for the videos modality."""

from celeste.parameters import ParameterMapper
from celeste.providers.bfl.videos.parameters import (
    AspectRatioMapper as _AspectRatioMapper,
)
from celeste.providers.bfl.videos.parameters import DraftMapper as _DraftMapper
from celeste.providers.bfl.videos.parameters import DurationMapper as _DurationMapper
from celeste.providers.bfl.videos.parameters import (
    FirstFrameMapper as _FirstFrameMapper,
)
from celeste.providers.bfl.videos.parameters import (
    GenerateAudioMapper as _GenerateAudioMapper,
)
from celeste.providers.bfl.videos.parameters import (
    KeyframesMapper as _KeyframesMapper,
)
from celeste.providers.bfl.videos.parameters import (
    LastFrameMapper as _LastFrameMapper,
)
from celeste.providers.bfl.videos.parameters import (
    ResolutionMapper as _ResolutionMapper,
)
from celeste.providers.bfl.videos.parameters import (
    SafetyToleranceMapper as _SafetyToleranceMapper,
)
from celeste.providers.bfl.videos.parameters import (
    StartVideoMapper as _StartVideoMapper,
)
from celeste.types import VideoContent

from ...parameters import VideoParameter


class AspectRatioMapper(_AspectRatioMapper):
    name = VideoParameter.ASPECT_RATIO


class DurationMapper(_DurationMapper):
    name = VideoParameter.DURATION


class ResolutionMapper(_ResolutionMapper):
    name = VideoParameter.RESOLUTION


class GenerateAudioMapper(_GenerateAudioMapper):
    name = VideoParameter.GENERATE_AUDIO


class DraftMapper(_DraftMapper):
    name = VideoParameter.DRAFT


class FirstFrameMapper(_FirstFrameMapper):
    name = VideoParameter.FIRST_FRAME


class LastFrameMapper(_LastFrameMapper):
    name = VideoParameter.LAST_FRAME


class KeyframesMapper(_KeyframesMapper):
    name = VideoParameter.KEYFRAMES


class StartVideoMapper(_StartVideoMapper):
    name = VideoParameter.START_VIDEO


class SafetyToleranceMapper(_SafetyToleranceMapper):
    name = VideoParameter.SAFETY_TOLERANCE


BFL_PARAMETER_MAPPERS: list[ParameterMapper[VideoContent]] = [
    AspectRatioMapper(),
    DurationMapper(),
    ResolutionMapper(),
    GenerateAudioMapper(),
    DraftMapper(),
    FirstFrameMapper(),
    LastFrameMapper(),
    KeyframesMapper(),
    StartVideoMapper(),
    SafetyToleranceMapper(),
]

__all__ = ["BFL_PARAMETER_MAPPERS"]
