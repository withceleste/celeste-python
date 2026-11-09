"""BFL FLUX API parameter mappers."""

from typing import Any

from celeste.constraints import ImagesConstraint, Int
from celeste.exceptions import ConstraintViolationError, ValidationError
from celeste.models import Model
from celeste.parameters import FieldMapper, ParameterMapper
from celeste.types import ImageContent, VideoContent

from .utils import add_input_images, encode_image


class AspectRatioMapper[Content](ParameterMapper[Content]):
    """Map native ratios or validated pixel dimensions for the BFL family."""

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request
        if model.id in (
            "flux-kontext-pro",
            "flux-kontext-max",
            "flux-pro-1.1-ultra",
            "flux-3-image",
            "flux-3-video",
        ):
            request["aspect_ratio"] = validated_value
        else:
            width, height = validated_value.split("x")
            request["width"] = Int()(width)
            request["height"] = Int()(height)
        return request


class PromptUpsamplingMapper(ParameterMapper[ImageContent]):
    """Map the prompt control supported by each BFL family."""

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        validated_value = self._validate_value(value, model)
        if validated_value is None or model.id.startswith("flux-2-klein-"):
            return request
        if model.id in ("flux-2-max", "flux-2-pro", "flux-2-pro-preview"):
            request["disable_pup"] = not validated_value
        else:
            request["prompt_upsampling"] = validated_value
        return request


class SeedMapper(FieldMapper[ImageContent]):
    """Map seed to BFL seed field."""

    field = "seed"


class ReferenceImagesMapper(ParameterMapper[ImageContent]):
    """Map all references to the model's BFL input image field."""

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        constraint = model.parameter_constraints.get(self.name)
        if (
            isinstance(constraint, ImagesConstraint)
            and constraint.max_count is not None
            and len(validated_value) + 1 > constraint.max_count
            and any(
                field in request for field in ("images", "input_image", "image_prompt")
            )
        ):
            msg = (
                f"{model.id} accepts at most {constraint.max_count} input images, "
                "including the primary edit image"
            )
            raise ConstraintViolationError(msg)

        return add_input_images(request, validated_value, model)


class SafetyToleranceMapper(FieldMapper[ImageContent]):
    """Map safety_tolerance to BFL safety_tolerance field."""

    field = "safety_tolerance"


class OutputFormatMapper(FieldMapper[ImageContent]):
    """Map output_format to BFL output_format field."""

    field = "output_format"


class StepsMapper(FieldMapper[ImageContent]):
    """Map steps to BFL steps field."""

    field = "steps"


class GuidanceMapper(FieldMapper[ImageContent]):
    """Map guidance to BFL guidance field."""

    field = "guidance"


class ResolutionMapper[Content](FieldMapper[Content]):
    """Map resolution to BFL resolution field."""

    field = "resolution"


class GroundingMapper(FieldMapper[ImageContent]):
    """Map grounding to BFL grounding field."""

    field = "grounding"


class DurationMapper(FieldMapper[VideoContent]):
    """Map duration to BFL duration field."""

    field = "duration"


class FirstFrameMapper(ParameterMapper[VideoContent]):
    """Map first_frame to the opening BFL keyframe in i2v mode."""

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request
        request["mode"] = "i2v"
        request["keyframes"] = [encode_image(validated_value)]
        return request


class LastFrameMapper(ParameterMapper[VideoContent]):
    """Map last_frame to the closing BFL keyframe after first_frame."""

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request
        if "keyframes" not in request:
            msg = "last_frame requires first_frame to be provided"
            raise ValidationError(msg)
        request["keyframes"].append(encode_image(validated_value))
        return request


__all__ = [
    "AspectRatioMapper",
    "DurationMapper",
    "FirstFrameMapper",
    "GroundingMapper",
    "GuidanceMapper",
    "LastFrameMapper",
    "OutputFormatMapper",
    "PromptUpsamplingMapper",
    "ReferenceImagesMapper",
    "ResolutionMapper",
    "SafetyToleranceMapper",
    "SeedMapper",
    "StepsMapper",
]
