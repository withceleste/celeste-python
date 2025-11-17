"""ByteDance parameter mappers for video generation."""

from typing import Any

from celeste import Model
from celeste.exceptions import ValidationError
from celeste.parameters import ParameterMapper
from celeste_video_generation.parameters import VideoGenerationParameter


class DurationMapper(ParameterMapper):
    """Map duration parameter to BytePlus ModelArk text prompt format.

    BytePlus ModelArk API expects parameters embedded in the text prompt:
    "prompt text --duration 5" instead of {"duration": 5}.

    All Seedance models support duration: 2-12 seconds.
    """

    name = VideoGenerationParameter.DURATION

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Append --duration parameter to text prompt in content array.

        Args:
            request: The request dictionary with content array.
            value: The duration value in seconds (integer).
            model: The model being used (provides constraints).

        Returns:
            Modified request with duration appended to text prompt.
        """
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        # BytePlus ModelArk uses content array with text type
        # Parameters must be embedded in the text field: "prompt --duration 5"
        content = request.get("content", [])
        for item in content:
            if item.get("type") == "text":
                text = item.get("text", "")
                # Append duration parameter to text prompt
                item["text"] = f"{text} --duration {validated_value}"
                break

        return request


class ResolutionMapper(ParameterMapper):
    """Map resolution parameter to BytePlus ModelArk text prompt format.

    BytePlus ModelArk API expects parameters embedded in the text prompt:
    "prompt text --resolution 720p" instead of {"resolution": "720p"}.

    Supported values:
    - All models: 480p, 720p, 1080p
    """

    name = VideoGenerationParameter.RESOLUTION

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Append --resolution parameter to text prompt in content array.

        Args:
            request: The request dictionary with content array.
            value: The resolution value (e.g., "720p").
            model: The model being used (provides constraints).

        Returns:
            Modified request with resolution appended to text prompt.
        """
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        # BytePlus ModelArk uses content array with text type
        # Parameters must be embedded in the text field: "prompt --resolution 720p"
        content = request.get("content", [])
        for item in content:
            if item.get("type") == "text":
                text = item.get("text", "")
                # Append resolution parameter to text prompt
                item["text"] = f"{text} --resolution {validated_value}"
                break

        return request


class ReferenceImagesMapper(ParameterMapper):
    """Map reference_images parameter to BytePlus ModelArk content array format."""

    name = VideoGenerationParameter.REFERENCE_IMAGES

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Add reference images to content array with reference_image role."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        content = request.setdefault("content", [])
        for img in validated_value:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": img.url,
                    },
                    "role": "reference_image",
                }
            )

        return request


class FirstFrameMapper(ParameterMapper):
    """Map first_frame parameter to BytePlus ModelArk content array format."""

    name = VideoGenerationParameter.FIRST_FRAME

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Add first frame image to content array with first_frame role."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        if not validated_value.url:
            msg = "ByteDance requires image URL (including data URIs) for first_frame. ImageArtifact must have url, data, or path"
            raise ValidationError(msg)

        content = request.setdefault("content", [])
        content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": validated_value.url,
                },
                "role": "first_frame",
            }
        )

        return request


class LastFrameMapper(ParameterMapper):
    """Map last_frame parameter to BytePlus ModelArk content array format."""

    name = VideoGenerationParameter.LAST_FRAME

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Add last frame image to content array with last_frame role."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        if not validated_value.url:
            msg = "ByteDance requires image URL (including data URIs) for last_frame. ImageArtifact must have url, data, or path"
            raise ValidationError(msg)

        content = request.setdefault("content", [])
        content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": validated_value.url,
                },
                "role": "last_frame",
            }
        )

        return request


BYTEDANCE_PARAMETER_MAPPERS: list[ParameterMapper] = [
    DurationMapper(),
    ResolutionMapper(),
    ReferenceImagesMapper(),
    FirstFrameMapper(),
    LastFrameMapper(),
]

__all__ = ["BYTEDANCE_PARAMETER_MAPPERS"]
