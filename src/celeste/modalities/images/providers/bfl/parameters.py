"""BFL parameter mappers for images modality."""

from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.providers.bfl.flux.parameters import (
    AspectRatioMapper as _AspectRatioMapper,
)
from celeste.providers.bfl.flux.parameters import (
    GroundingMapper as _GroundingMapper,
)
from celeste.providers.bfl.flux.parameters import (
    GuidanceMapper as _GuidanceMapper,
)
from celeste.providers.bfl.flux.parameters import (
    ImagePromptMapper as _ImagePromptMapper,
)
from celeste.providers.bfl.flux.parameters import (
    ImagesMapper as _ImagesMapper,
)
from celeste.providers.bfl.flux.parameters import (
    InputImageMapper as _InputImageMapper,
)
from celeste.providers.bfl.flux.parameters import (
    OutputFormatMapper as _OutputFormatMapper,
)
from celeste.providers.bfl.flux.parameters import (
    PromptUpsamplingMapper as _PromptUpsamplingMapper,
)
from celeste.providers.bfl.flux.parameters import (
    ResolutionMapper as _ResolutionMapper,
)
from celeste.providers.bfl.flux.parameters import (
    SafetyToleranceMapper as _SafetyToleranceMapper,
)
from celeste.providers.bfl.flux.parameters import (
    SeedMapper as _SeedMapper,
)
from celeste.providers.bfl.flux.parameters import (
    StepsMapper as _StepsMapper,
)
from celeste.providers.bfl.flux.utils import add_dimensions
from celeste.types import ImageContent

from ...parameters import ImageParameter
from .models import (
    BFL_FLUX1_ASPECT_RATIO_MODELS,
    BFL_FLUX2_DISABLE_PUP_MODELS,
    BFL_FLUX2_KLEIN_MODELS,
)


class Flux3AspectRatioMapper(_AspectRatioMapper[ImageContent]):
    name = ImageParameter.ASPECT_RATIO


class Flux3SeedMapper(_SeedMapper):
    name = ImageParameter.SEED


class Flux3SafetyToleranceMapper(_SafetyToleranceMapper):
    name = ImageParameter.SAFETY_TOLERANCE


class Flux3OutputFormatMapper(_OutputFormatMapper):
    name = ImageParameter.OUTPUT_FORMAT


class Flux3StepsMapper(_StepsMapper):
    name = ImageParameter.STEPS


class Flux3ReferenceImagesMapper(_ImagesMapper):
    name = ImageParameter.REFERENCE_IMAGES


class Flux3QualityMapper(_ResolutionMapper[ImageContent]):
    name = ImageParameter.QUALITY


class Flux3GroundingMapper(_GroundingMapper):
    name = ImageParameter.GROUNDING


BFL_FLUX3_PARAMETER_MAPPERS: list[ParameterMapper[ImageContent]] = [
    Flux3AspectRatioMapper(),
    Flux3SeedMapper(),
    Flux3SafetyToleranceMapper(),
    Flux3OutputFormatMapper(),
    Flux3StepsMapper(),
    Flux3ReferenceImagesMapper(),
    Flux3QualityMapper(),
    Flux3GroundingMapper(),
]


class Flux2AspectRatioMapper(ParameterMapper[ImageContent]):
    """Map WxH aspect_ratio to BFL's width and height parameters."""

    name = ImageParameter.ASPECT_RATIO

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request
        return add_dimensions(request, validated_value)


class Flux2PromptUpsamplingMapper(_PromptUpsamplingMapper):
    """Map prompt_upsampling to BFL's prompt_upsampling or disable_pup parameter."""

    name = ImageParameter.PROMPT_UPSAMPLING

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Invert to disable_pup where the model takes it; drop on FLUX.2 [klein]."""
        if model.id in BFL_FLUX2_KLEIN_MODELS:
            return request
        request = super().map(request, value, model)
        if model.id in BFL_FLUX2_DISABLE_PUP_MODELS and "prompt_upsampling" in request:
            request["disable_pup"] = not request.pop("prompt_upsampling")
        return request


class Flux2SeedMapper(_SeedMapper):
    name = ImageParameter.SEED


class Flux2SafetyToleranceMapper(_SafetyToleranceMapper):
    name = ImageParameter.SAFETY_TOLERANCE


class Flux2OutputFormatMapper(_OutputFormatMapper):
    name = ImageParameter.OUTPUT_FORMAT


class Flux2StepsMapper(_StepsMapper):
    name = ImageParameter.STEPS


class Flux2GuidanceMapper(_GuidanceMapper):
    name = ImageParameter.GUIDANCE


class Flux2ReferenceImagesMapper(_InputImageMapper):
    name = ImageParameter.REFERENCE_IMAGES


BFL_FLUX2_PARAMETER_MAPPERS: list[ParameterMapper[ImageContent]] = [
    Flux2AspectRatioMapper(),
    Flux2PromptUpsamplingMapper(),
    Flux2SeedMapper(),
    Flux2SafetyToleranceMapper(),
    Flux2OutputFormatMapper(),
    Flux2StepsMapper(),
    Flux2GuidanceMapper(),
    Flux2ReferenceImagesMapper(),
]


class KontextAspectRatioMapper(_AspectRatioMapper[ImageContent]):
    name = ImageParameter.ASPECT_RATIO


class KontextPromptUpsamplingMapper(_PromptUpsamplingMapper):
    name = ImageParameter.PROMPT_UPSAMPLING


class KontextSeedMapper(_SeedMapper):
    name = ImageParameter.SEED


class KontextSafetyToleranceMapper(_SafetyToleranceMapper):
    name = ImageParameter.SAFETY_TOLERANCE


class KontextOutputFormatMapper(_OutputFormatMapper):
    name = ImageParameter.OUTPUT_FORMAT


class KontextReferenceImagesMapper(_InputImageMapper):
    name = ImageParameter.REFERENCE_IMAGES


BFL_KONTEXT_PARAMETER_MAPPERS: list[ParameterMapper[ImageContent]] = [
    KontextAspectRatioMapper(),
    KontextPromptUpsamplingMapper(),
    KontextSeedMapper(),
    KontextSafetyToleranceMapper(),
    KontextOutputFormatMapper(),
    KontextReferenceImagesMapper(),
]


class Flux1AspectRatioMapper(_AspectRatioMapper[ImageContent]):
    """Map aspect_ratio to BFL's aspect_ratio or width and height parameters."""

    name = ImageParameter.ASPECT_RATIO

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Send a native ratio where the model takes one, else WxH dimensions."""
        if model.id in BFL_FLUX1_ASPECT_RATIO_MODELS:
            return super().map(request, value, model)
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request
        return add_dimensions(request, validated_value)


class Flux1PromptUpsamplingMapper(_PromptUpsamplingMapper):
    name = ImageParameter.PROMPT_UPSAMPLING


class Flux1SeedMapper(_SeedMapper):
    name = ImageParameter.SEED


class Flux1SafetyToleranceMapper(_SafetyToleranceMapper):
    name = ImageParameter.SAFETY_TOLERANCE


class Flux1OutputFormatMapper(_OutputFormatMapper):
    name = ImageParameter.OUTPUT_FORMAT


class Flux1StepsMapper(_StepsMapper):
    name = ImageParameter.STEPS


class Flux1GuidanceMapper(_GuidanceMapper):
    name = ImageParameter.GUIDANCE


class Flux1ReferenceImagesMapper(_ImagePromptMapper):
    name = ImageParameter.REFERENCE_IMAGES


BFL_FLUX1_PARAMETER_MAPPERS: list[ParameterMapper[ImageContent]] = [
    Flux1AspectRatioMapper(),
    Flux1PromptUpsamplingMapper(),
    Flux1SeedMapper(),
    Flux1SafetyToleranceMapper(),
    Flux1OutputFormatMapper(),
    Flux1StepsMapper(),
    Flux1GuidanceMapper(),
    Flux1ReferenceImagesMapper(),
]

__all__ = [
    "BFL_FLUX1_PARAMETER_MAPPERS",
    "BFL_FLUX2_PARAMETER_MAPPERS",
    "BFL_FLUX3_PARAMETER_MAPPERS",
    "BFL_KONTEXT_PARAMETER_MAPPERS",
]
