"""Google parameter mappers for video generation."""

from typing import Any

from celeste.exceptions import ValidationError
from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste_video_generation.parameters import VideoGenerationParameter


class AspectRatioMapper(ParameterMapper):
    """Map aspect_ratio parameter to Google API format."""

    name = VideoGenerationParameter.ASPECT_RATIO

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

        # Transform to provider-specific request format
        request.setdefault("parameters", {})["aspectRatio"] = validated_value
        return request


class ResolutionMapper(ParameterMapper):
    """Map resolution parameter to Google API format."""

    name = VideoGenerationParameter.RESOLUTION

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform resolution into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        # Transform to provider-specific request format
        request.setdefault("parameters", {})["resolution"] = validated_value
        return request


class DurationSecondsMapper(ParameterMapper):
    """Map duration parameter to Google API format."""

    name = VideoGenerationParameter.DURATION

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform duration into provider request."""
        # Coerce to integer if string provided (for backward compatibility)
        if isinstance(value, str):
            value = int(value)

        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        # Transform to provider-specific request format (API expects integer)
        request.setdefault("parameters", {})["durationSeconds"] = validated_value
        return request


class ReferenceImagesMapper(ParameterMapper):
    """Map reference_images parameter to Google API format."""

    name = VideoGenerationParameter.REFERENCE_IMAGES

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform reference_images into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        reference_images = []
        for img in validated_value:
            ref_image: dict[str, Any] = {
                "image": {},
                "referenceType": "asset",
            }

            # Check if URL is base64 data URI
            if img.url and img.url.startswith("data:image/"):
                # Extract base64 data from data URI
                header, encoded = img.url.split(",", 1)
                mime_type = header.split(":")[1].split(";")[0]
                ref_image["image"]["bytesBase64Encoded"] = encoded
                ref_image["image"]["mimeType"] = mime_type
            else:
                msg = "ImageArtifact must have data or path for reference images (base64 encoding required)"
                raise ValidationError(msg)

            reference_images.append(ref_image)

        request.setdefault("instances", [{}])[0]["referenceImages"] = reference_images
        return request


class FirstFrameMapper(ParameterMapper):
    """Map first_frame parameter to Google API format."""

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

        # Check if URL is base64 data URI
        if validated_value.url and validated_value.url.startswith("data:image/"):
            # Extract base64 data from data URI
            header, encoded = validated_value.url.split(",", 1)
            mime_type = header.split(":")[1].split(";")[0]

            # Set image in instances[0].image
            request.setdefault("instances", [{}])[0]["image"] = {
                "bytesBase64Encoded": encoded,
                "mimeType": mime_type,
            }
        else:
            msg = "ImageArtifact must have data or path for first_frame (base64 encoding required)"
            raise ValidationError(msg)

        return request


class LastFrameMapper(ParameterMapper):
    """Map last_frame parameter to Google API format."""

    name = VideoGenerationParameter.LAST_FRAME

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform last_frame into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        # Check if first_frame (image) exists - lastFrame requires image per API docs
        instances = request.get("instances", [{}])
        if not instances or "image" not in instances[0]:
            msg = "last_frame requires first_frame to be provided"
            raise ValidationError(msg)

        # Check if URL is base64 data URI
        if validated_value.url and validated_value.url.startswith("data:image/"):
            # Extract base64 data from data URI
            header, encoded = validated_value.url.split(",", 1)
            mime_type = header.split(":")[1].split(";")[0]

            # Set lastFrame in instances[0] to match image structure
            request.setdefault("instances", [{}])[0]["lastFrame"] = {
                "bytesBase64Encoded": encoded,
                "mimeType": mime_type,
            }
        else:
            msg = "ImageArtifact must have data or path for last_frame (base64 encoding required)"
            raise ValidationError(msg)

        return request


GOOGLE_PARAMETER_MAPPERS: list[ParameterMapper] = [
    AspectRatioMapper(),
    ResolutionMapper(),
    DurationSecondsMapper(),
    ReferenceImagesMapper(),
    FirstFrameMapper(),
    LastFrameMapper(),
]

__all__ = ["GOOGLE_PARAMETER_MAPPERS"]
