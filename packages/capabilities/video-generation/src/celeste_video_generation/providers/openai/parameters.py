"""OpenAI parameter mappers for video generation."""

from typing import Any

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

        # Validate but don't transform (size derivation happens in client)
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

        # Validate but don't transform (size derivation happens in client)
        return request


class DurationSecondsMapper(ParameterMapper):
    """Map duration parameter to OpenAI API format.

    Converts user-facing int to API-required string.
    """

    name = VideoGenerationParameter.DURATION

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform duration into provider request."""
        # Coerce int to string (user provides int, API expects string)
        if isinstance(value, int):
            value = str(value)

        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        # Transform to provider-specific request format (top-level field)
        request["seconds"] = validated_value
        return request


class FirstFrameMapper(ParameterMapper):
    """Map first_frame parameter to OpenAI API format.

    OpenAI Sora's input_reference acts as the first frame of the video.
    Image must match target video resolution.
    Note: OpenAI uses multipart/form-data for file uploads.
    """

    name = VideoGenerationParameter.FIRST_FRAME

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform first_frame into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["input_reference"] = validated_value
        return request


OPENAI_PARAMETER_MAPPERS: list[ParameterMapper] = [
    AspectRatioMapper(),
    ResolutionMapper(),
    DurationSecondsMapper(),
    FirstFrameMapper(),
]

__all__ = ["OPENAI_PARAMETER_MAPPERS"]
