"""fal models for segmentation modality."""

from celeste.constraints import Bool, ImageConstraint, Range
from celeste.core import Modality, Operation, Provider
from celeste.models import Model

from ...parameters import SegmentationParameter

MODELS: list[Model] = [
    Model(
        id="fal-ai/sam-3/image-rle",
        provider=Provider.FAL,
        display_name="SAM 3 Image RLE",
        operations={Modality.SEGMENTATION: {Operation.SEGMENT}},
        parameter_constraints={
            SegmentationParameter.IMAGE: ImageConstraint(),
            SegmentationParameter.MAX_MASKS: Range(min=1, max=32),
            SegmentationParameter.INCLUDE_SCORES: Bool(),
            SegmentationParameter.INCLUDE_BOXES: Bool(),
            SegmentationParameter.RETURN_MULTIPLE_MASKS: Bool(),
        },
    ),
    Model(
        id="fal-ai/sam-3-1/image-rle",
        provider=Provider.FAL,
        display_name="SAM 3.1 Image RLE",
        operations={Modality.SEGMENTATION: {Operation.SEGMENT}},
        parameter_constraints={
            SegmentationParameter.IMAGE: ImageConstraint(),
            SegmentationParameter.MAX_MASKS: Range(min=1, max=32),
            SegmentationParameter.INCLUDE_SCORES: Bool(),
            SegmentationParameter.INCLUDE_BOXES: Bool(),
            SegmentationParameter.RETURN_MULTIPLE_MASKS: Bool(),
        },
    ),
]

__all__ = ["MODELS"]
