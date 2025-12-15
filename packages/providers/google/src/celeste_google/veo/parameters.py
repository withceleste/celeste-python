"""Google Veo API parameter mappers."""

from typing import Any

from celeste import image_to_data_uri
from celeste.exceptions import ValidationError
from celeste.models import Model
from celeste.parameters import ParameterMapper


class AspectRatioMapper(ParameterMapper):
    """Map aspect_ratio to Google Veo parameters.aspectRatio field."""

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
    """Map resolution to Google Veo parameters.resolution field."""

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
    """Map duration to Google Veo parameters.durationSeconds field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform duration into provider request."""
        # Coerce to integer if string provided
        if isinstance(value, str):
            value = int(value)

        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        # Transform to provider-specific request format (API expects integer)
        request.setdefault("parameters", {})["durationSeconds"] = validated_value
        return request


class ReferenceImagesMapper(ParameterMapper):
    """Map reference_images to Google Veo instances.referenceImages field."""

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
        # Validated value is list[ImageArtifact] based on capability constraints
        for img in validated_value:
            ref_image: dict[str, Any] = {
                "image": {},
                "referenceType": "asset",
            }

            # Convert to data URI using core utility
            try:
                data_uri = image_to_data_uri(img)

                # Extract base64 data from data URI
                header, encoded = data_uri.split(",", 1)
                mime_type = header.split(":")[1].split(";")[0]

                ref_image["image"]["bytesBase64Encoded"] = encoded
                ref_image["image"]["mimeType"] = mime_type
            except (ValueError, IndexError, OSError):
                msg = "Failed to process reference image. Ensure valid data/path/url."
                raise ValidationError(msg) from None

            reference_images.append(ref_image)

        request.setdefault("instances", [{}])[0]["referenceImages"] = reference_images
        return request


class FirstFrameMapper(ParameterMapper):
    """Map first_frame to Google Veo instances.image field."""

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

        # Convert to data URI using core utility
        try:
            data_uri = image_to_data_uri(validated_value)

            # Extract base64 data from data URI
            header, encoded = data_uri.split(",", 1)
            mime_type = header.split(":")[1].split(";")[0]

            # Set image in instances[0].image
            request.setdefault("instances", [{}])[0]["image"] = {
                "bytesBase64Encoded": encoded,
                "mimeType": mime_type,
            }
        except (ValueError, IndexError, OSError):
            msg = "Failed to process first_frame. Ensure valid data/path/url."
            raise ValidationError(msg) from None

        return request


class LastFrameMapper(ParameterMapper):
    """Map last_frame to Google Veo instances.lastFrame field."""

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

        # Convert to data URI using core utility
        try:
            data_uri = image_to_data_uri(validated_value)

            # Extract base64 data from data URI
            header, encoded = data_uri.split(",", 1)
            mime_type = header.split(":")[1].split(";")[0]

            # Set lastFrame in instances[0] to match image structure
            request.setdefault("instances", [{}])[0]["lastFrame"] = {
                "bytesBase64Encoded": encoded,
                "mimeType": mime_type,
            }
        except (ValueError, IndexError, OSError):
            msg = "Failed to process last_frame. Ensure valid data/path/url."
            raise ValidationError(msg) from None

        return request


__all__ = [
    "AspectRatioMapper",
    "DurationSecondsMapper",
    "FirstFrameMapper",
    "LastFrameMapper",
    "ReferenceImagesMapper",
    "ResolutionMapper",
]
