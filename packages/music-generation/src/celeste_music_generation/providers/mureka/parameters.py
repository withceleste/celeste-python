"""Parameter mappers for Mureka provider."""

from typing import Any

from celeste import Model
from celeste.parameters import ParameterMapper
from celeste_music_generation.parameters import MusicGenerationParameter


class MurekaLyricsMapper(ParameterMapper):
    """Map lyrics parameter to Mureka API.

    Note: Only add lyrics if non-empty. Empty lyrics will cause API error.
    Lyrics are only supported on mureka-6 and mureka-7.5 models.
    """

    name = MusicGenerationParameter.LYRICS

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        validated_value = self._validate_value(value, model)
        # Only add lyrics if it's a non-empty string
        if validated_value is not None and isinstance(validated_value, str) and validated_value.strip():
            request["lyrics"] = validated_value.strip()
        return request


class MurekaNMapper(ParameterMapper):
    """Map n parameter to Mureka API."""

    name = MusicGenerationParameter.N

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        validated_value = self._validate_value(value, model)
        if validated_value is not None:
            request["n"] = validated_value
        return request


class MurekaReferenceIdMapper(ParameterMapper):
    """Map reference_id parameter to Mureka API."""

    name = MusicGenerationParameter.REFERENCE_ID

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        validated_value = self._validate_value(value, model)
        if validated_value is not None:
            request["reference_id"] = validated_value
        return request


class MurekaVocalIdMapper(ParameterMapper):
    """Map vocal_id parameter to Mureka API."""

    name = MusicGenerationParameter.VOCAL_ID

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        validated_value = self._validate_value(value, model)
        if validated_value is not None:
            request["vocal_id"] = validated_value
        return request


class MurekaMelodyIdMapper(ParameterMapper):
    """Map melody_id parameter to Mureka API."""

    name = MusicGenerationParameter.MELODY_ID

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        validated_value = self._validate_value(value, model)
        if validated_value is not None:
            request["melody_id"] = validated_value
        return request


class MurekaStreamMapper(ParameterMapper):
    """Map stream parameter to Mureka API."""

    name = MusicGenerationParameter.STREAM

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        validated_value = self._validate_value(value, model)
        if validated_value is not None:
            request["stream"] = validated_value
        return request


MUREKA_PARAMETER_MAPPERS: list[ParameterMapper] = [
    MurekaLyricsMapper(),
    MurekaNMapper(),
    MurekaReferenceIdMapper(),
    MurekaVocalIdMapper(),
    MurekaMelodyIdMapper(),
    MurekaStreamMapper(),
]

__all__ = ["MUREKA_PARAMETER_MAPPERS"]
