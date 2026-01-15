"""BytePlus Videos API parameter mappers."""

from typing import Any

from celeste.exceptions import ValidationError
from celeste.models import Model
from celeste.parameters import ParameterMapper


class DurationMapper(ParameterMapper):
    """Map duration parameter to BytePlus text prompt format.

    Appends --duration to the text prompt.
    Supported values: 2-12 seconds.
    """

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Transform duration into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        content = request.get("content", [])
        for item in content:
            if item.get("type") == "text":
                text = item.get("text", "")
                item["text"] = f"{text} --duration {validated_value}"
                break

        return request


class ResolutionMapper(ParameterMapper):
    """Map resolution parameter to BytePlus text prompt format.

    Appends --resolution to the text prompt.
    Supported values: 480p, 720p, 1080p.
    """

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Transform resolution into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        content = request.get("content", [])
        for item in content:
            if item.get("type") == "text":
                text = item.get("text", "")
                item["text"] = f"{text} --resolution {validated_value}"
                break

        return request


class AspectRatioMapper(ParameterMapper):
    """Map aspect_ratio parameter to BytePlus text prompt format.

    Appends --ratio to the text prompt.
    Supported values: 16:9, 4:3, 1:1, 3:4, 9:16, 21:9, adaptive.
    """

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Transform aspect_ratio into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        content = request.get("content", [])
        for item in content:
            if item.get("type") == "text":
                text = item.get("text", "")
                item["text"] = f"{text} --ratio {validated_value}"
                break

        return request


class ReferenceImagesMapper(ParameterMapper):
    """Map reference_images to BytePlus content array format.

    Adds images with role="reference_image" to the content array.
    """

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Transform reference_images into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        content = request.setdefault("content", [])
        for img in validated_value:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": img.url},
                    "role": "reference_image",
                }
            )

        return request


class FirstFrameMapper(ParameterMapper):
    """Map first_frame to BytePlus content array format.

    Adds image with role="first_frame" to the content array.
    """

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Transform first_frame into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        if not validated_value.url:
            msg = "BytePlus requires image URL for first_frame."
            raise ValidationError(msg) from None

        content = request.setdefault("content", [])
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": validated_value.url},
                "role": "first_frame",
            }
        )

        return request


class LastFrameMapper(ParameterMapper):
    """Map last_frame to BytePlus content array format.

    Adds image with role="last_frame" to the content array.
    """

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        """Transform last_frame into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        if not validated_value.url:
            msg = "BytePlus requires image URL for last_frame."
            raise ValidationError(msg) from None

        content = request.setdefault("content", [])
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": validated_value.url},
                "role": "last_frame",
            }
        )

        return request


__all__ = [
    "AspectRatioMapper",
    "DurationMapper",
    "FirstFrameMapper",
    "LastFrameMapper",
    "ReferenceImagesMapper",
    "ResolutionMapper",
]
