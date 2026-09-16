"""BFL parameter mappers for images modality."""

from celeste.parameters import ParameterMapper
from celeste.providers.bfl.images.parameters import (
    AspectRatioMapper as _AspectRatioMapper,
)
from celeste.providers.bfl.images.parameters import (
    GuidanceMapper as _GuidanceMapper,
)
from celeste.providers.bfl.images.parameters import (
    OutputFormatMapper as _OutputFormatMapper,
)
from celeste.providers.bfl.images.parameters import (
    PromptUpsamplingMapper as _PromptUpsamplingMapper,
)
from celeste.providers.bfl.images.parameters import (
    ReferenceImagesMapper as _ReferenceImagesMapper,
)
from celeste.providers.bfl.images.parameters import (
    SafetyToleranceMapper as _SafetyToleranceMapper,
)
from celeste.providers.bfl.images.parameters import (
    SeedMapper as _SeedMapper,
)
from celeste.providers.bfl.images.parameters import (
    StepsMapper as _StepsMapper,
)
from celeste.types import ImageContent

from ...parameters import ImageParameter


class AspectRatioMapper(_AspectRatioMapper):
    name = ImageParameter.ASPECT_RATIO


class PromptUpsamplingMapper(_PromptUpsamplingMapper):
    name = ImageParameter.PROMPT_UPSAMPLING


class SeedMapper(_SeedMapper):
    name = ImageParameter.SEED


class SafetyToleranceMapper(_SafetyToleranceMapper):
    name = ImageParameter.SAFETY_TOLERANCE


class OutputFormatMapper(_OutputFormatMapper):
    name = ImageParameter.OUTPUT_FORMAT


class StepsMapper(_StepsMapper):
    name = ImageParameter.STEPS


class GuidanceMapper(_GuidanceMapper):
    name = ImageParameter.GUIDANCE


class ReferenceImagesMapper(_ReferenceImagesMapper):
    name = ImageParameter.REFERENCE_IMAGES


BFL_PARAMETER_MAPPERS: list[ParameterMapper[ImageContent]] = [
    AspectRatioMapper(),
    PromptUpsamplingMapper(),
    SeedMapper(),
    SafetyToleranceMapper(),
    OutputFormatMapper(),
    StepsMapper(),
    GuidanceMapper(),
    ReferenceImagesMapper(),
]

__all__ = ["BFL_PARAMETER_MAPPERS"]
