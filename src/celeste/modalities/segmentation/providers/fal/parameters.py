"""fal parameter mappers for segmentation modality."""

from celeste.parameters import FieldMapper, ParameterMapper
from celeste.types import SegmentationContent

from ...parameters import SegmentationParameter


class PointPromptsMapper(FieldMapper[SegmentationContent]):
    name = SegmentationParameter.POINT_PROMPTS
    field = "point_prompts"


class BoxPromptsMapper(FieldMapper[SegmentationContent]):
    name = SegmentationParameter.BOX_PROMPTS
    field = "box_prompts"


class MaxMasksMapper(FieldMapper[SegmentationContent]):
    name = SegmentationParameter.MAX_MASKS
    field = "max_masks"


class IncludeScoresMapper(FieldMapper[SegmentationContent]):
    name = SegmentationParameter.INCLUDE_SCORES
    field = "include_scores"


class IncludeBoxesMapper(FieldMapper[SegmentationContent]):
    name = SegmentationParameter.INCLUDE_BOXES
    field = "include_boxes"


class ReturnMultipleMasksMapper(FieldMapper[SegmentationContent]):
    name = SegmentationParameter.RETURN_MULTIPLE_MASKS
    field = "return_multiple_masks"


FAL_PARAMETER_MAPPERS: list[ParameterMapper[SegmentationContent]] = [
    PointPromptsMapper(),
    BoxPromptsMapper(),
    MaxMasksMapper(),
    IncludeScoresMapper(),
    IncludeBoxesMapper(),
    ReturnMultipleMasksMapper(),
]

__all__ = ["FAL_PARAMETER_MAPPERS"]
