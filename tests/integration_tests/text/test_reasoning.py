import pytest

from celeste import Modality, Provider, create_client
from celeste.modalities.text import TextChunk, TextOutput

MODELS: list[tuple[Provider, str, dict[str, int | str]]] = [
    (Provider.ANTHROPIC, "claude-haiku-4-5", {"thinking_budget": 1024}),
    (Provider.COHERE, "command-a-plus-05-2026", {"thinking_budget": 1024}),
    (Provider.GOOGLE, "gemini-2.5-flash-lite", {"thinking_level": "high"}),
    (Provider.MISTRAL, "mistral-small-2603", {"thinking_budget": "high"}),
    (Provider.OPENAI, "gpt-5-nano", {"thinking_budget": "low"}),
    (Provider.XAI, "grok-3-mini", {"thinking_budget": "low"}),
]


@pytest.mark.parametrize(("provider", "model", "thinking"), MODELS)
async def test_reasoning_generate(
    provider: Provider, model: str, thinking: dict[str, int | str]
) -> None:
    client = create_client(modality=Modality.TEXT, provider=provider, model=model)

    response = await client.generate(
        prompt="What is 15 * 37? Think step by step.",
        max_tokens=2000,
        **thinking,
    )

    assert isinstance(response, TextOutput)
    assert response.reasoning
    assert response.content


@pytest.mark.parametrize(("provider", "model", "thinking"), MODELS)
async def test_reasoning_stream(
    provider: Provider, model: str, thinking: dict[str, int | str]
) -> None:
    client = create_client(modality=Modality.TEXT, provider=provider, model=model)

    chunks = [
        chunk
        async for chunk in client.stream.generate(
            prompt="What is 15 * 37? Think step by step.",
            max_tokens=2000,
            **thinking,
        )
    ]

    assert chunks
    assert all(isinstance(chunk, TextChunk) for chunk in chunks)
    assert any(chunk.reasoning for chunk in chunks)
