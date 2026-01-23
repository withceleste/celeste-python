"""Ollama parameter mappers for images modality."""

from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.providers.ollama.generate.parameters import (
    HeightMapper as _HeightMapper,
)
from celeste.providers.ollama.generate.parameters import (
    NegativePromptMapper as _NegativePromptMapper,
)
from celeste.providers.ollama.generate.parameters import (
    SeedMapper as _SeedMapper,
)
from celeste.providers.ollama.generate.parameters import (
    StepsMapper as _StepsMapper,
)
from celeste.providers.ollama.generate.parameters import (
    WidthMapper as _WidthMapper,
)

from ...parameters import ImageParameter


class AspectRatioMapper(ParameterMapper):
    """Map aspect_ratio to Ollama's width and height parameters.

    Parses 'WxH' string and delegates to native mappers.
    """

    name = ImageParameter.ASPECT_RATIO

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

        request = _WidthMapper().map(request, width, model)
        request = _HeightMapper().map(request, height, model)
        return request


class StepsMapper(_StepsMapper):
    """Map steps parameter to Ollama's steps field."""

    name = ImageParameter.STEPS


class SeedMapper(_SeedMapper):
    """Map seed parameter to Ollama's options.seed field."""

    name = ImageParameter.SEED


class NegativePromptMapper(_NegativePromptMapper):
    """Map negative_prompt parameter to Ollama's negative_prompt field."""

    name = ImageParameter.NEGATIVE_PROMPT


OLLAMA_PARAMETER_MAPPERS: list[ParameterMapper] = [
    AspectRatioMapper(),
    StepsMapper(),
    SeedMapper(),
    NegativePromptMapper(),
]

__all__ = ["OLLAMA_PARAMETER_MAPPERS"]
