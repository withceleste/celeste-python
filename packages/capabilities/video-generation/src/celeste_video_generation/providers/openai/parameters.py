"""OpenAI Videos parameter mappers for video generation."""

from typing import Any

from celeste_openai.videos.parameters import (
    InputReferenceMapper as _InputReferenceMapper,
)
from celeste_openai.videos.parameters import (
    SecondsMapper as _SecondsMapper,
)

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste_video_generation.parameters import VideoGenerationParameter


class AspectRatioMapper(ParameterMapper):
    """Validate aspect_ratio parameter.

    Validation only - size derivation happens in client.
    """

    name = VideoGenerationParameter.ASPECT_RATIO

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Validate aspect_ratio parameter."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request
        return request


class ResolutionMapper(ParameterMapper):
    """Validate resolution parameter.

    Validation only - size derivation happens in client.
    """

    name = VideoGenerationParameter.RESOLUTION

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Validate resolution parameter."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request
        return request


class DurationMapper(_SecondsMapper):
    """Map duration parameter to OpenAI API format."""

    name = VideoGenerationParameter.DURATION


class FirstFrameMapper(_InputReferenceMapper):
    """Map first_frame parameter to OpenAI API format."""

    name = VideoGenerationParameter.FIRST_FRAME


OPENAI_PARAMETER_MAPPERS: list[ParameterMapper] = [
    AspectRatioMapper(),
    ResolutionMapper(),
    DurationMapper(),
    FirstFrameMapper(),
]

__all__ = ["OPENAI_PARAMETER_MAPPERS"]
