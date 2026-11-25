"""BFL parameter mappers for images modality."""

from celeste.parameters import ParameterMapper
from celeste.providers.bfl.images.parameters import (
    AspectRatioMapper as _AspectRatioMapper,
    GroundingMapper as _GroundingMapper,
    GuidanceMapper as _GuidanceMapper,
    OutputFormatMapper as _OutputFormatMapper,
    PromptUpsamplingMapper as _PromptUpsamplingMapper,
    ReferenceImagesMapper as _ReferenceImagesMapper,
    ResolutionMapper as _ResolutionMapper,
    SafetyToleranceMapper as _SafetyToleranceMapper,
    SeedMapper as _SeedMapper,
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


class QualityMapper(_ResolutionMapper):
    name = ImageParameter.QUALITY


class GroundingMapper(_GroundingMapper):
    name = ImageParameter.GROUNDING


BFL_PARAMETER_MAPPERS: list[ParameterMapper[ImageContent]] = [
    AspectRatioMapper(),
    PromptUpsamplingMapper(),
    SeedMapper(),
    SafetyToleranceMapper(),
    OutputFormatMapper(),
    StepsMapper(),
    GuidanceMapper(),
    ReferenceImagesMapper(),
    QualityMapper(),
    GroundingMapper(),
]

__all__ = ["BFL_PARAMETER_MAPPERS"]
