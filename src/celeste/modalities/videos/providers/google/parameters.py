"""Google parameter mappers for videos."""

from celeste.parameters import ParameterMapper
from celeste.providers.google.interactions.parameters import (
    AspectRatioMapper as _InteractionsAspectRatioMapper,
)
from celeste.providers.google.interactions.parameters import (
    DurationMapper as _InteractionsDurationMapper,
)
from celeste.providers.google.interactions.parameters import (
    FirstFrameMapper as _InteractionsFirstFrameMapper,
)
from celeste.providers.google.interactions.parameters import (
    LastFrameMapper as _InteractionsLastFrameMapper,
)
from celeste.providers.google.interactions.parameters import (
    ReferenceImagesMapper as _InteractionsReferenceImagesMapper,
)
from celeste.providers.google.veo.parameters import (
    AspectRatioMapper as _VeoAspectRatioMapper,
)
from celeste.providers.google.veo.parameters import (
    DurationSecondsMapper as _VeoDurationSecondsMapper,
)
from celeste.providers.google.veo.parameters import (
    FirstFrameMapper as _VeoFirstFrameMapper,
)
from celeste.providers.google.veo.parameters import (
    LastFrameMapper as _VeoLastFrameMapper,
)
from celeste.providers.google.veo.parameters import (
    ReferenceImagesMapper as _VeoReferenceImagesMapper,
)
from celeste.providers.google.veo.parameters import (
    ResolutionMapper as _VeoResolutionMapper,
)
from celeste.types import VideoContent

from ...parameters import VideoParameter


class VeoAspectRatioMapper(_VeoAspectRatioMapper):
    """Map aspect_ratio to Google Veo's aspectRatio parameter."""

    name = VideoParameter.ASPECT_RATIO


class VeoResolutionMapper(_VeoResolutionMapper):
    """Map resolution to Google Veo's resolution parameter."""

    name = VideoParameter.RESOLUTION


class VeoDurationMapper(_VeoDurationSecondsMapper):
    """Map duration to Google Veo's durationSeconds parameter."""

    name = VideoParameter.DURATION


class VeoReferenceImagesMapper(_VeoReferenceImagesMapper):
    """Map reference_images to Google Veo's referenceImages parameter."""

    name = VideoParameter.REFERENCE_IMAGES


class VeoFirstFrameMapper(_VeoFirstFrameMapper):
    """Map first_frame to Google Veo's image parameter."""

    name = VideoParameter.FIRST_FRAME


class VeoLastFrameMapper(_VeoLastFrameMapper):
    """Map last_frame to Google Veo's lastFrame parameter."""

    name = VideoParameter.LAST_FRAME


GOOGLE_VEO_PARAMETER_MAPPERS: list[ParameterMapper[VideoContent]] = [
    VeoAspectRatioMapper(),
    VeoResolutionMapper(),
    VeoDurationMapper(),
    VeoReferenceImagesMapper(),
    VeoFirstFrameMapper(),
    VeoLastFrameMapper(),
]


class InteractionsAspectRatioMapper(_InteractionsAspectRatioMapper[VideoContent]):
    """Map aspect_ratio to Google Interactions response_format.aspect_ratio."""

    name = VideoParameter.ASPECT_RATIO


class InteractionsDurationMapper(_InteractionsDurationMapper):
    """Map duration to Google Interactions response_format.duration."""

    name = VideoParameter.DURATION


class InteractionsFirstFrameMapper(_InteractionsFirstFrameMapper):
    """Map first_frame to Google Interactions input content."""

    name = VideoParameter.FIRST_FRAME


class InteractionsLastFrameMapper(_InteractionsLastFrameMapper):
    """Map last_frame to Google Interactions input content."""

    name = VideoParameter.LAST_FRAME


class InteractionsReferenceImagesMapper(_InteractionsReferenceImagesMapper):
    """Map reference_images to Google Interactions input content."""

    name = VideoParameter.REFERENCE_IMAGES


GOOGLE_INTERACTIONS_PARAMETER_MAPPERS: list[ParameterMapper[VideoContent]] = [
    InteractionsAspectRatioMapper(),
    InteractionsDurationMapper(),
    InteractionsFirstFrameMapper(),
    InteractionsLastFrameMapper(),
    InteractionsReferenceImagesMapper(),
]

__all__ = ["GOOGLE_INTERACTIONS_PARAMETER_MAPPERS", "GOOGLE_VEO_PARAMETER_MAPPERS"]
