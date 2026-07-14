import pytest

from celeste import Modality, Provider, create_client
from celeste.modalities.text import TextChunk, TextOutput

MODELS: list[tuple[Provider, str, int | str]] = [
    (Provider.ANTHROPIC, "claude-haiku-4-5", 1024),
    (Provider.COHERE, "command-a-plus-05-2026", 1024),
    (Provider.GOOGLE, "gemini-2.5-flash-lite", 1024),
    (Provider.MISTRAL, "mistral-small-2603", "low"),
    (Provider.OPENAI, "gpt-5-nano", "low"),
    (Provider.XAI, "grok-3-mini", "low"),
]


@pytest.mark.parametrize(("provider", "model", "thinking_budget"), MODELS)
async def test_reasoning_generate(
    provider: Provider, model: str, thinking_budget: int | str
) -> None:
    client = create_client(modality=Modality.TEXT, provider=provider, model=model)

    response = await client.generate(
        prompt="What is 15 * 37? Think step by step.",
        max_tokens=2000,
        thinking_budget=thinking_budget,
    )

    assert isinstance(response, TextOutput)
    assert response.reasoning
    assert response.content


@pytest.mark.parametrize(("provider", "model", "thinking_budget"), MODELS)
async def test_reasoning_stream(
    provider: Provider, model: str, thinking_budget: int | str
) -> None:
    client = create_client(modality=Modality.TEXT, provider=provider, model=model)

    chunks = [
        chunk
        async for chunk in client.stream.generate(
            prompt="What is 15 * 37? Think step by step.",
            max_tokens=2000,
            thinking_budget=thinking_budget,
        )
    ]

    assert chunks
    assert all(isinstance(chunk, TextChunk) for chunk in chunks)
    assert any(chunk.reasoning for chunk in chunks)
