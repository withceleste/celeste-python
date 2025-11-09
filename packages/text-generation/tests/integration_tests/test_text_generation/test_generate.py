"""Integration tests for text generation across all providers."""

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
async def test_generate(provider: Provider, model: str, parameters: dict) -> None:
    """Test text generation with max_tokens parameter across all providers.

    This test demonstrates that the unified API works identically across
    all providers using the same code - proving the abstraction value.
    """
    # Import here to avoid circular import during pytest collection
    from celeste_text_generation import TextGenerationOutput, TextGenerationUsage

    # Arrange
    client = create_client(
        capability=Capability.TEXT_GENERATION,
        provider=provider,
    )
    prompt = "Hi"
    max_tokens = 30

    # Act
    response = await client.generate(
        prompt=prompt,
        model=model,
        max_tokens=max_tokens,
        **parameters,
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
