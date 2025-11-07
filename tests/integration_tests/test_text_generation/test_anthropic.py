"""Integration tests for Anthropic text generation."""

import pytest
from celeste_text_generation import TextGenerationOutput, TextGenerationUsage
from celeste_text_generation.client import TextGenerationClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_anthropic_generate(anthropic_client: TextGenerationClient) -> None:
    """Test Anthropic text generation with max_tokens parameter."""
    # Arrange
    prompt = "Hi"
    model = "claude-haiku-4-5"
    max_tokens = 30

    # Act
    response = await anthropic_client.generate(
        prompt=prompt,
        model=model,
        max_tokens=max_tokens,
    )

    # Assert
    assert isinstance(response, TextGenerationOutput), (
        f"Expected TextGenerationOutput, got {type(response)}"
    )
    assert isinstance(response.content, str), (
        f"Expected str content, got {type(response.content)}"
    )
    assert len(response.content) > 0, f"Content is empty: {response.content!r}"

    # Validate usage metrics
    assert isinstance(response.usage, TextGenerationUsage), (
        f"Expected TextGenerationUsage, got {type(response.usage)}"
    )
    assert response.usage.output_tokens is not None, (
        f"output_tokens is None. Usage: {response.usage.model_dump()}"
    )
    assert response.usage.output_tokens <= max_tokens, (
        f"output_tokens ({response.usage.output_tokens}) should not exceed "
        f"max_tokens ({max_tokens}). Usage: {response.usage.model_dump()}"
    )
    assert response.usage.input_tokens is not None, (
        f"input_tokens is None. Usage: {response.usage.model_dump()}"
    )
    assert response.usage.input_tokens > 0, (
        f"input_tokens should be > 0, got {response.usage.input_tokens}. Usage: {response.usage.model_dump()}"
    )
    assert response.usage.total_tokens is not None, (
        f"total_tokens is None. Usage: {response.usage.model_dump()}"
    )
