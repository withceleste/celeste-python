"""Integration tests for text generation streaming across all providers."""

import pytest

from celeste import Capability, Provider, create_client


@pytest.mark.parametrize(
    ("provider", "model", "parameters"),
    [
        (Provider.OPENAI, "gpt-3.5-turbo", {}),
        (Provider.ANTHROPIC, "claude-haiku-4-5", {}),
        (Provider.GOOGLE, "gemini-2.5-flash-lite", {"thinking_budget": 0}),
        (Provider.MISTRAL, "mistral-tiny", {}),
        (Provider.COHERE, "command-a-03-2025", {}),
    ],
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_stream(provider: Provider, model: str, parameters: dict) -> None:
    """Test text generation streaming with max_tokens parameter across all providers.

    This test demonstrates that the unified streaming API works identically across
    all providers using the same code - proving the abstraction value.
    """
    # Import here to avoid circular import during pytest collection
    from celeste_text_generation import (
        TextGenerationChunk,
        TextGenerationFinishReason,
        TextGenerationOutput,
        TextGenerationStream,
        TextGenerationUsage,
    )

    # Arrange
    client = create_client(
        capability=Capability.TEXT_GENERATION,
        provider=provider,
    )
    prompt = "Hi"
    max_tokens = 30

    # Act - Create stream
    stream = client.stream(
        prompt=prompt,
        model=model,
        max_tokens=max_tokens,
        **parameters,
    )

    # Assert 1: Stream Creation
    assert isinstance(stream, TextGenerationStream), (
        f"Expected TextGenerationStream, got {type(stream)}"
    )

    # Act - Iterate chunks
    chunks: list[TextGenerationChunk] = []
    async for chunk in stream:
        # Assert 2: Chunk Structure
        assert isinstance(chunk, TextGenerationChunk), (
            f"Expected TextGenerationChunk, got {type(chunk)}"
        )
        assert isinstance(chunk.content, str), (
            f"Expected str content, got {type(chunk.content)}"
        )
        if chunk.finish_reason is not None:
            assert isinstance(chunk.finish_reason, TextGenerationFinishReason), (
                f"Expected TextGenerationFinishReason, got {type(chunk.finish_reason)}"
            )
        if chunk.usage is not None:
            assert isinstance(chunk.usage, TextGenerationUsage), (
                f"Expected TextGenerationUsage, got {type(chunk.usage)}"
            )
        chunks.append(chunk)

    # Assert 3: Content Accumulation
    assert len(chunks) > 0, "No chunks were yielded from stream"
    accumulated_content = "".join(chunk.content for chunk in chunks)
    assert len(accumulated_content) > 0, f"Accumulated content is empty: {chunks!r}"

    # Assert 4: Final Output
    output = stream.output
    assert isinstance(output, TextGenerationOutput), (
        f"Expected TextGenerationOutput, got {type(output)}"
    )
    assert isinstance(output.content, str), (
        f"Expected str content, got {type(output.content)}"
    )
    assert output.content == accumulated_content, (
        f"Output content doesn't match accumulated chunks: "
        f"{output.content!r} != {accumulated_content!r}"
    )

    # Assert 5: Usage Metrics
    assert isinstance(output.usage, TextGenerationUsage), (
        f"Expected TextGenerationUsage, got {type(output.usage)}"
    )

    # Assert 6: Finish Reason
    assert chunks[-1].finish_reason is not None, "Final chunk should have finish_reason"
    assert output.finish_reason is not None, (
        "Output should have finish_reason as direct field"
    )
    assert isinstance(output.finish_reason, TextGenerationFinishReason), (
        f"Expected TextGenerationFinishReason, got {type(output.finish_reason)}"
    )
