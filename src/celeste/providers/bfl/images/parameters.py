"""BFL Images API parameter mappers."""

from typing import Any

from celeste.constraints import ImagesConstraint, Int
from celeste.exceptions import ConstraintViolationError
from celeste.models import Model
from celeste.parameters import FieldMapper, ParameterMapper
from celeste.types import ImageContent

from .utils import add_reference_images


class AspectRatioMapper(ParameterMapper[ImageContent]):
    """Map native ratios or validated pixel dimensions for the BFL family."""

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request
        if model.id in ("flux-kontext-pro", "flux-kontext-max", "flux-pro-1.1-ultra"):
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
    """Map all references to BFL's numbered input fields."""

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        constraint = model.parameter_constraints.get(self.name)
        if (
            "input_image" in request
            and isinstance(constraint, ImagesConstraint)
            and constraint.max_count is not None
            and len(validated_value) + 1 > constraint.max_count
        ):
            msg = (
                f"{model.id} accepts at most {constraint.max_count} input images, "
                "including the primary edit image"
            )
            raise ConstraintViolationError(msg)

        return add_reference_images(request, validated_value)


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


__all__ = [
    "AspectRatioMapper",
    "GuidanceMapper",
    "OutputFormatMapper",
    "PromptUpsamplingMapper",
    "ReferenceImagesMapper",
    "SafetyToleranceMapper",
    "SeedMapper",
    "StepsMapper",
]
