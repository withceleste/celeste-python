"""Input and output types for generation operations."""

import inspect
import types
from typing import Any, get_args, get_origin

from pydantic import BaseModel, Field

from celeste.artifacts import AudioArtifact, ImageArtifact, VideoArtifact
from celeste.constraints import Constraint
from celeste.core import InputType


class Input(BaseModel):
    """Base class for capability-specific input types."""

    pass


class FinishReason(BaseModel):
    """Base class for capability-specific finish reasons (used in streaming chunks and outputs)."""

    reason: str | None = None


class Usage(BaseModel):
    """Base class for capability-specific usage metrics."""

    pass


class Output[Content](BaseModel):
    """Base output class with generic content type."""

    content: Content
    usage: Usage = Field(default_factory=Usage)
    finish_reason: FinishReason | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Chunk[Content](BaseModel):
    """Incremental chunk from streaming response with generic content type."""

    content: Content
    finish_reason: FinishReason | None = None
    usage: Usage | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


# Centralized mapping: field type → InputType
INPUT_TYPE_MAPPING: dict[type, InputType] = {
    str: InputType.TEXT,
    ImageArtifact: InputType.IMAGE,
    VideoArtifact: InputType.VIDEO,
    AudioArtifact: InputType.AUDIO,
}


def _extract_input_type(param_type: type) -> InputType | None:
    """Extract InputType from a type, handling unions and generics.

    Args:
        param_type: The type annotation to inspect.

    Returns:
        InputType if found in the type or its nested types, None otherwise.
    """
    # Direct match
    if param_type in INPUT_TYPE_MAPPING:
        return INPUT_TYPE_MAPPING[param_type]

    # Handle union types (X | Y) and generics (list[X])
    origin = get_origin(param_type)
    if origin is types.UnionType or origin is not None:
        for arg in get_args(param_type):
            result = _extract_input_type(arg)
            if result is not None:
                return result

    return None


def get_constraint_input_type(constraint: Constraint) -> InputType | None:
    """Get InputType from constraint's __call__ signature.

    Introspects the constraint's __call__ method to find what artifact type
    it accepts, then maps to InputType using INPUT_TYPE_MAPPING.

    Args:
        constraint: The constraint to inspect.

    Returns:
        InputType if the constraint accepts a mapped artifact type, None otherwise.
    """
    annotations = inspect.get_annotations(constraint.__call__, eval_str=True)
    for param_type in annotations.values():
        result = _extract_input_type(param_type)
        if result is not None:
            return result
    return None


__all__ = [
    "INPUT_TYPE_MAPPING",
    "Chunk",
    "FinishReason",
    "Input",
    "Output",
    "Usage",
    "get_constraint_input_type",
]
