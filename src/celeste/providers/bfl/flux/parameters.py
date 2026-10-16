"""BFL FLUX API parameter mappers."""

from typing import Any, ClassVar

from celeste.constraints import ImagesConstraint
from celeste.exceptions import ConstraintViolationError
from celeste.models import Model
from celeste.parameters import FieldMapper, ParameterMapper
from celeste.types import ImageContent

from .utils import add_input_images


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


__all__ = [
    "AspectRatioMapper",
    "GroundingMapper",
    "GuidanceMapper",
    "ImagePromptMapper",
    "ImagesMapper",
    "InputImageMapper",
    "OutputFormatMapper",
    "PromptUpsamplingMapper",
    "ReferenceImagesMapper",
    "ResolutionMapper",
    "SafetyToleranceMapper",
    "SeedMapper",
    "StepsMapper",
]
