"""Input and output types for generation operations."""

from typing import Any

from pydantic import BaseModel, Field


class Input(BaseModel):
    """Base class for capability-specific input types.

    Each capability defines its own Input subclass that specifies
    the required fields for that capability's generate() method.
    Input classes serve as the capability-level contract that all
    providers must accept, enabling UI/CLI introspection and validation.

    Examples:
        TextGenerationInput(prompt: str)
        VideoIntelligenceInput(video: VideoArtifact, prompt: str)
        EmbeddingsInput(text: str | list[str])
    """

    pass


class FinishReason(BaseModel):
    """Base class for capability-specific finish reasons.

    Each capability defines its own FinishReason subclass with
    provider-reported fields (reason string, metadata, flags).

    Examples:
        TextGenerationFinishReason(reason: str, stop_sequence: str | None)
        ImageGenerationFinishReason(reason: str, safety_filtered: bool)
    """

    pass


class Usage(BaseModel):
    """Base class for capability-specific usage metrics.

    Each capability defines its own Usage subclass with
    provider-reported metrics (tokens, credits, frames, etc.).

    Examples:
        TextGenerationUsage(input_tokens: int, output_tokens: int)
        VideoGenerationUsage(frame_count: int, duration_seconds: float)
    """

    pass


class Output[Content](BaseModel):
    """Base output class with generic content type.

    Attributes:
        content: The generated content (type varies by capability).
        usage: Capability-specific Usage subclass (e.g., TextGenerationUsage).
               Providers MUST use concrete Usage types in practice. Empty base
               Usage class serves as fallback when usage data unavailable.
        metadata: Additional provider-specific metadata.
    """

    content: Content
    usage: Usage = Field(default_factory=Usage)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Chunk[Content](BaseModel):
    """Incremental chunk from streaming response with generic content type.

    Attributes:
        content: Incremental content delta (type varies by capability).
        finish_reason: Optional - typically only present in final chunk when
                      stream completes.
        usage: Optional - providers typically report usage only in final chunk.
               May be None for intermediate chunks.
        metadata: Additional provider-specific metadata for this chunk.
    """

    content: Content
    finish_reason: FinishReason | None = None
    usage: Usage | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


__all__ = ["Chunk", "FinishReason", "Input", "Output", "Usage"]

