"""Integration tests for Google text generation."""

import pytest
from celeste_text_generation import TextGenerationOutput, TextGenerationUsage
from celeste_text_generation.client import TextGenerationClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_google_generate(google_client: TextGenerationClient) -> None:
    """Test Google text generation with max_tokens parameter."""
    # Arrange
    prompt = "Hi"
    model = "gemini-2.5-flash-lite"
    max_tokens = 30

    # Act
    response = await google_client.generate(
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
    # Google may not always return usage metrics, so be lenient
    if response.usage.output_tokens is not None:
        assert response.usage.output_tokens <= max_tokens, (
            f"output_tokens ({response.usage.output_tokens}) should not exceed "
            f"max_tokens ({max_tokens}). Usage: {response.usage.model_dump()}"
        )
    if response.usage.input_tokens is not None:
        assert response.usage.input_tokens > 0, (
            f"input_tokens should be > 0, got {response.usage.input_tokens}. Usage: {response.usage.model_dump()}"
        )
