"""Parameters for segmentation modality."""

from enum import StrEnum
from typing import Annotated, Literal, NotRequired, TypedDict

from pydantic import Field

from celeste.parameters import Parameters


class PointPrompt(TypedDict):
    """Point prompt for visual segmentation."""

    x: int
    y: int
    label: Literal[0, 1]
    object_id: NotRequired[int]


class BoxPrompt(TypedDict):
    """Box prompt for visual segmentation (xyxy pixels)."""

    x_min: int
    y_min: int
    x_max: int
    y_max: int
    object_id: NotRequired[int]


class SegmentationParameter(StrEnum):
    """Parameter names for segmentation."""

    IMAGE = "image"
    POINT_PROMPTS = "point_prompts"
    BOX_PROMPTS = "box_prompts"
    MAX_MASKS = "max_masks"
    INCLUDE_SCORES = "include_scores"
    INCLUDE_BOXES = "include_boxes"
    RETURN_MULTIPLE_MASKS = "return_multiple_masks"


class SegmentationParameters(Parameters, total=False):
    """Parameters for segmentation operations."""

    point_prompts: Annotated[
        list[PointPrompt] | None,
        Field(description="Point prompts with foreground/background labels."),
    ]
    box_prompts: Annotated[
        list[BoxPrompt] | None,
        Field(description="Box prompts in xyxy pixel coordinates."),
    ]
    max_masks: Annotated[
        int | None,
        Field(description="Maximum masks when return_multiple_masks is enabled."),
    ]
    include_scores: Annotated[
        bool | None,
        Field(description="Include per-mask confidence scores."),
    ]
    include_boxes: Annotated[
        bool | None,
        Field(description="Include per-mask bounding boxes."),
    ]
    return_multiple_masks: Annotated[
        bool | None,
        Field(description="Return multiple masks up to max_masks."),
    ]


__all__ = [
    "BoxPrompt",
    "PointPrompt",
    "SegmentationParameter",
    "SegmentationParameters",
]
