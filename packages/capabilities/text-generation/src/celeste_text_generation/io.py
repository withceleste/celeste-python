"""Input and output types for text generation."""

from celeste.io import Chunk, FinishReason, Input, Output, Usage


class TextGenerationInput(Input):
    """Input for text generation operations."""

    prompt: str


class TextGenerationFinishReason(FinishReason):
    """Text generation finish reason.

    Stores raw provider reason. Providers map their values in implementation.
    """

    reason: str


class TextGenerationUsage(Usage):
    """Text generation usage metrics.

    All fields optional since providers vary.
    """

    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    billed_tokens: int | None = None
    cached_tokens: int | None = None
    reasoning_tokens: int | None = None


class TextGenerationOutput[Content](Output[Content]):
    """Output with text or structured content."""

    pass


class TextGenerationChunk(Chunk[str]):
    """Typed chunk for text generation streaming.

    Content is incremental text delta.
    """

    finish_reason: TextGenerationFinishReason | None = None
    usage: TextGenerationUsage | None = None


__all__ = [
    "TextGenerationChunk",
    "TextGenerationFinishReason",
    "TextGenerationInput",
    "TextGenerationOutput",
    "TextGenerationUsage",
]
