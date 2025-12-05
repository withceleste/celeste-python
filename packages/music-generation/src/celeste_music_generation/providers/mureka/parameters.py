"""Parameter mappers for Mureka provider."""

from typing import Any

from celeste import Model
from celeste.parameters import ParameterMapper
from celeste_music_generation.parameters import MusicGenerationParameter


class MurekaDurationMapper(ParameterMapper):
    """Map duration parameter to Mureka API."""

    name = MusicGenerationParameter.DURATION

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        validated_value = self._validate_value(value, model)
        if validated_value is not None:
            request["duration"] = validated_value
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


class MurekaQualityMapper(ParameterMapper):
    """Map quality parameter to Mureka API."""

    name = MusicGenerationParameter.QUALITY

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        validated_value = self._validate_value(value, model)
        if validated_value is not None:
            request["quality"] = validated_value
        return request


class MurekaStyleMapper(ParameterMapper):
    """Map style parameter to Mureka API."""

    name = MusicGenerationParameter.STYLE

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        validated_value = self._validate_value(value, model)
        if validated_value is not None:
            request["style"] = validated_value
        return request


class MurekaGenreMapper(ParameterMapper):
    """Map genre parameter to Mureka API."""

    name = MusicGenerationParameter.GENRE

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        validated_value = self._validate_value(value, model)
        if validated_value is not None:
            request["genre"] = validated_value
        return request


MUREKA_PARAMETER_MAPPERS: list[ParameterMapper] = [
    MurekaDurationMapper(),
    MurekaStreamMapper(),
    MurekaQualityMapper(),
    MurekaStyleMapper(),
    MurekaGenreMapper(),
]

__all__ = ["MUREKA_PARAMETER_MAPPERS"]
