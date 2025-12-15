"""Integration tests for speech generation streaming across all providers."""

import pytest

from celeste import Capability, Provider, create_client


@pytest.mark.parametrize(
    ("provider", "model", "parameters"),
    [
        # Only ElevenLabs currently supports streaming for speech generation
        # OpenAI and Google TTS do not support streaming in the same way
        (
            Provider.ELEVENLABS,
            "eleven_flash_v2_5",
            {"voice": "Rachel", "output_format": "mp3_44100_128"},
        ),
    ],
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_stream(provider: Provider, model: str, parameters: dict) -> None:
    """Test speech generation streaming across supported providers.

    Verifies that we receive audio chunks and can assemble them.
    """
    # Import here to avoid circular import during pytest collection
    from celeste_speech_generation import (
        SpeechGenerationChunk,
        SpeechGenerationUsage,
    )

    # Arrange
    client = create_client(
        capability=Capability.SPEECH_GENERATION,
        provider=provider,
        model=model,
    )
    text = "Hello, this is a streaming test."

    # Act
    chunks = []
    async for chunk in client.stream(
        text=text,
        **parameters,
    ):
        assert isinstance(chunk, SpeechGenerationChunk)
        chunks.append(chunk)

    # Assert
    assert len(chunks) > 0, "No chunks received"
    total_size = sum(len(chunk.content) for chunk in chunks)
    assert total_size > 0, "Total audio size is 0"

    # Verify usage if present in any chunk
    has_usage = any(chunk.usage is not None for chunk in chunks)
    if has_usage:
        last_usage = next(c.usage for c in reversed(chunks) if c.usage)
        assert isinstance(last_usage, SpeechGenerationUsage)
