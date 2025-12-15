"""BFL Images parameter mappers for image generation.

AspectRatioMapper is defined locally (handles "WxH" → width/height transformation).
Other mappers subclass from provider and add capability-specific `name` attribute.
"""

from typing import Any

from celeste_bfl.images.parameters import (
    GuidanceMapper as _GuidanceMapper,
)
from celeste_bfl.images.parameters import (
    HeightMapper as _HeightMapper,
)
from celeste_bfl.images.parameters import (
    OutputFormatMapper as _OutputFormatMapper,
)
from celeste_bfl.images.parameters import (
    PromptUpsamplingMapper as _PromptUpsamplingMapper,
)
from celeste_bfl.images.parameters import (
    SafetyToleranceMapper as _SafetyToleranceMapper,
)
from celeste_bfl.images.parameters import (
    SeedMapper as _SeedMapper,
)
from celeste_bfl.images.parameters import (
    StepsMapper as _StepsMapper,
)
from celeste_bfl.images.parameters import (
    WidthMapper as _WidthMapper,
)

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste_image_generation.parameters import ImageGenerationParameter


class AspectRatioMapper(ParameterMapper):
    """Map aspect_ratio to BFL width/height parameters.

    Converts 'WxH' string to width/height, rounded to nearest multiple of 16.
    Delegates to provider's WidthMapper and HeightMapper for the actual mapping.
    """

    name = ImageGenerationParameter.ASPECT_RATIO

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform aspect_ratio into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        parts = validated_value.split("x")
        width = int(parts[0])
        height = int(parts[1])

        # Round to nearest multiple of 16 as required by BFL API
        width = ((width + 8) // 16) * 16
        height = ((height + 8) // 16) * 16

        # Delegate to provider mappers
        request = _WidthMapper().map(request, width, model)
        request = _HeightMapper().map(request, height, model)
        return request


class PromptUpsamplingMapper(_PromptUpsamplingMapper):
    name = ImageGenerationParameter.PROMPT_UPSAMPLING


class SeedMapper(_SeedMapper):
    name = ImageGenerationParameter.SEED


class SafetyToleranceMapper(_SafetyToleranceMapper):
    name = ImageGenerationParameter.SAFETY_TOLERANCE


class OutputFormatMapper(_OutputFormatMapper):
    name = ImageGenerationParameter.OUTPUT_FORMAT


class StepsMapper(_StepsMapper):
    name = ImageGenerationParameter.STEPS


class GuidanceMapper(_GuidanceMapper):
    name = ImageGenerationParameter.GUIDANCE


BFL_PARAMETER_MAPPERS: list[ParameterMapper] = [
    AspectRatioMapper(),
    PromptUpsamplingMapper(),
    SeedMapper(),
    SafetyToleranceMapper(),
    OutputFormatMapper(),
    StepsMapper(),
    GuidanceMapper(),
]

__all__ = ["BFL_PARAMETER_MAPPERS"]
