"""Integration tests for speech generation across all providers."""

import pytest

from celeste import Capability, Provider, create_client


@pytest.mark.parametrize(
    ("provider", "model", "parameters"),
    [
        (Provider.OPENAI, "tts-1", {"voice": "alloy", "output_format": "mp3"}),
        (
            Provider.GOOGLE,
            "gemini-2.5-flash-tts",
            {"voice": "Zephyr", "speed": 1.0},
        ),
        (
            Provider.ELEVENLABS,
            "eleven_flash_v2_5",
            {"voice": "Rachel", "output_format": "mp3_44100_128"},
        ),
        (Provider.GRADIUM, "default", {}),
    ],
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_generate(provider: Provider, model: str, parameters: dict) -> None:
    """Test speech generation with voice parameter across all providers.

    This test demonstrates that the unified API works identically across
    all providers using the same code - proving the abstraction value.
    Uses cheapest models to minimize costs.
    """
    # Import here to avoid circular import during pytest collection
    from celeste_speech_generation import (
        SpeechGenerationOutput,
        SpeechGenerationUsage,
    )

    from celeste.artifacts import AudioArtifact

    # Arrange
    client = create_client(
        capability=Capability.SPEECH_GENERATION,
        provider=provider,
        model=model,
    )
    text = "Hello, this is a test of the Celeste speech generation capability."

    # Act
    response = await client.generate(
        text=text,
        **parameters,
    )

    # Assert
    assert isinstance(response, SpeechGenerationOutput), (
        f"Expected SpeechGenerationOutput, got {type(response)}"
    )
    assert isinstance(response.content, AudioArtifact), (
        f"Expected AudioArtifact content, got {type(response.content)}"
    )
    assert response.content.has_content, (
        f"AudioArtifact has no content (data/path): {response.content}"
    )
    assert response.content.data is not None, "Audio data is None"
    assert len(response.content.data) > 0, "Audio data is empty"

    # Validate usage metrics
    assert isinstance(response.usage, SpeechGenerationUsage), (
        f"Expected SpeechGenerationUsage, got {type(response.usage)}"
    )
