"""BFL FLUX API parameter mappers."""

from typing import Any, ClassVar

from celeste.constraints import ImagesConstraint
from celeste.exceptions import ConstraintViolationError, ValidationError
from celeste.models import Model
from celeste.parameters import FieldMapper, ParameterMapper
from celeste.types import ImageContent, VideoContent

from .utils import add_input_images, encode_image


class AspectRatioMapper[Content](FieldMapper[Content]):
    """Map aspect_ratio to BFL aspect_ratio field."""

    field = "aspect_ratio"


class PromptUpsamplingMapper(FieldMapper[ImageContent]):
    """Map prompt_upsampling to BFL prompt_upsampling field."""

    field = "prompt_upsampling"


class SeedMapper(FieldMapper[ImageContent]):
    """Map seed to BFL seed field."""

    field = "seed"


class ReferenceImagesMapper(ParameterMapper[ImageContent]):
    """Map all references to a BFL input image field after the edit image."""

    field: ClassVar[str]

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
            and self.field in request
        ):
            msg = (
                f"{model.id} accepts at most {constraint.max_count} input images, "
                "including the primary edit image"
            )
            raise ConstraintViolationError(msg)

        return add_input_images(request, validated_value, self.field)


class InputImageMapper(ReferenceImagesMapper):
    """Map references to BFL input_image, input_image_2, ... fields."""

    field = "input_image"


class ImagesMapper(ReferenceImagesMapper):
    """Map references to the BFL images list."""

    field = "images"


class ImagePromptMapper(ReferenceImagesMapper):
    """Map references to the BFL image_prompt field."""

    field = "image_prompt"


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
    "ImagePromptMapper",
    "ImagesMapper",
    "InputImageMapper",
    "LastFrameMapper",
    "OutputFormatMapper",
    "PromptUpsamplingMapper",
    "ReferenceImagesMapper",
    "ResolutionMapper",
    "SafetyToleranceMapper",
    "SeedMapper",
    "StepsMapper",
]
