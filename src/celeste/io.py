"""Input and output types for generation operations."""

from typing import Any

from pydantic import BaseModel, Field

from celeste.core import Capability


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


_inputs: dict[Capability, type[Input]] = {}


def register_input(capability: Capability, input_class: type[Input]) -> None:
    """Register an Input class for a capability."""
    _inputs[capability] = input_class


def get_input_class(capability: Capability) -> type[Input]:
    """Get the registered Input class for a capability."""
    if capability not in _inputs:
        msg = f"No Input class registered for capability: {capability}"
        raise KeyError(msg)
    return _inputs[capability]


__all__ = [
    "Chunk",
    "FinishReason",
    "Input",
    "Output",
    "Usage",
    "get_input_class",
    "register_input",
]
