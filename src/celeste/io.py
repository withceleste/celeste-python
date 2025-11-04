"""Input and output types for generation operations."""

from typing import Any

from pydantic import BaseModel, Field


class Input(BaseModel):
    """Base class for capability-specific input types."""

    pass


class FinishReason(BaseModel):
    """Base class for capability-specific finish reasons (used in streaming chunks)."""

    pass


class Usage(BaseModel):
    """Base class for capability-specific usage metrics."""

    pass


class Output[Content](BaseModel):
    """Base output class with generic content type."""

    content: Content
    usage: Usage = Field(default_factory=Usage)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Chunk[Content](BaseModel):
    """Incremental chunk from streaming response with generic content type."""

    content: Content
    finish_reason: FinishReason | None = None
    usage: Usage | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


__all__ = ["Chunk", "FinishReason", "Input", "Output", "Usage"]
