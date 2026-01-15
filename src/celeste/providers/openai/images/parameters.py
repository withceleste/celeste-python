"""OpenAI Images API parameter mappers."""

from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper


class SizeMapper(ParameterMapper):
    """Map size to OpenAI size field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform size into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["size"] = validated_value
        return request


class PartialImagesMapper(ParameterMapper):
    """Map partial_images to OpenAI partial_images field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform partial_images into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["partial_images"] = validated_value
        return request


class QualityMapper(ParameterMapper):
    """Map quality to OpenAI quality field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform quality into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["quality"] = validated_value
        return request


class BackgroundMapper(ParameterMapper):
    """Map background to OpenAI background field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform background into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["background"] = validated_value
        return request


class OutputFormatMapper(ParameterMapper):
    """Map output_format to OpenAI output_format field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform output_format into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["output_format"] = validated_value
        return request


class StyleMapper(ParameterMapper):
    """Map style to OpenAI style field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform style into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["style"] = validated_value
        return request


class ModerationMapper(ParameterMapper):
    """Map moderation to OpenAI moderation field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform moderation into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["moderation"] = validated_value
        return request


class OutputCompressionMapper(ParameterMapper):
    """Map output_compression to OpenAI output_compression field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform output_compression into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["output_compression"] = validated_value
        return request


__all__ = [
    "BackgroundMapper",
    "ModerationMapper",
    "OutputCompressionMapper",
    "OutputFormatMapper",
    "PartialImagesMapper",
    "QualityMapper",
    "SizeMapper",
    "StyleMapper",
]
