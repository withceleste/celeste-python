"""BFL Videos API parameter mappers."""

from typing import Any

from celeste.exceptions import ValidationError
from celeste.models import Model
from celeste.parameters import FieldMapper, ParameterMapper
from celeste.providers.bfl.utils import encode_artifact


class AspectRatioMapper[Content](FieldMapper[Content]):
    """Map aspect_ratio to the BFL aspect_ratio field."""

    field = "aspect_ratio"


class DurationMapper[Content](FieldMapper[Content]):
    """Map duration to the BFL duration field."""

    field = "duration"


class ResolutionMapper[Content](ParameterMapper[Content]):
    """Map unified resolution tiers to BFL resolution classes."""

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Transform resolution into BFL's hd/fhd value."""
        validated_value = self._validate_value(value, model)
        if validated_value is not None:
            request["resolution"] = {"720p": "hd", "1080p": "fhd"}[validated_value]
        return request


class GenerateAudioMapper[Content](FieldMapper[Content]):
    """Map generate_audio to the BFL generate_audio field."""

    field = "generate_audio"


class DraftMapper[Content](FieldMapper[Content]):
    """Map draft to the BFL draft field."""

    field = "draft"


class FirstFrameMapper[Content](ParameterMapper[Content]):
    """Map first_frame to the first BFL keyframe."""

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Transform first_frame into a BFL keyframes list."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request
        _select_media_mode(request, "i2v")
        request["keyframes"] = [encode_artifact(validated_value)]
        return request


class LastFrameMapper[Content](ParameterMapper[Content]):
    """Append last_frame to BFL keyframes."""

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Transform last_frame into the final BFL keyframe."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request
        keyframes = request.get("keyframes")
        if not isinstance(keyframes, list) or not keyframes:
            msg = "last_frame requires first_frame to be provided"
            raise ValidationError(msg)
        keyframes.append(encode_artifact(validated_value))
        return request


class KeyframesMapper[Content](ParameterMapper[Content]):
    """Map typed keyframes to BFL image or timestamp-image values."""

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Transform VideoKeyframe values into BFL keyframes."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request
        if "keyframes" in request:
            msg = "keyframes cannot be combined with first_frame or last_frame"
            raise ValidationError(msg)
        _select_media_mode(request, "i2v")

        timed = validated_value[0].timestamp is not None
        request["keyframes"] = [
            [keyframe.timestamp, encode_artifact(keyframe.image)]
            if timed
            else encode_artifact(keyframe.image)
            for keyframe in validated_value
        ]
        return request


class StartVideoMapper[Content](ParameterMapper[Content]):
    """Map start_video to BFL video continuation input."""

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Transform start_video into the BFL start_video field."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request
        _select_media_mode(request, "v2v")
        request["start_video"] = encode_artifact(validated_value)
        return request


class SafetyToleranceMapper[Content](FieldMapper[Content]):
    """Map safety_tolerance to the BFL field."""

    field = "safety_tolerance"


def _select_media_mode(request: dict[str, Any], mode: str) -> None:
    """Select one mutually exclusive BFL media generation mode."""
    current = request.get("mode")
    if current not in {None, "t2v", mode}:
        msg = f"{mode} inputs cannot be combined with {current} inputs"
        raise ValidationError(msg)
    request["mode"] = mode


__all__ = [
    "AspectRatioMapper",
    "DraftMapper",
    "DurationMapper",
    "FirstFrameMapper",
    "GenerateAudioMapper",
    "KeyframesMapper",
    "LastFrameMapper",
    "ResolutionMapper",
    "SafetyToleranceMapper",
    "StartVideoMapper",
]
