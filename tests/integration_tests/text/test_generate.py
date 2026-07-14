import pytest

from celeste import Modality, Provider, create_client
from celeste.modalities.text import TextChunk, TextOutput, TextUsage
from celeste.providers.google.auth import GoogleADC

MODELS = [
    (Provider.ANTHROPIC, "claude-haiku-4-5"),
    (Provider.COHERE, "command-r7b-12-2024"),
    (Provider.DEEPSEEK, "deepseek-chat"),
    (Provider.GOOGLE, "gemini-2.5-flash-lite"),
    (Provider.GROQ, "llama-3.1-8b-instant"),
    (Provider.HUGGINGFACE, "Qwen/Qwen3-4B-Instruct-2507"),
    (Provider.MISTRAL, "mistral-tiny"),
    (Provider.MOONSHOT, "kimi-k2-0711-preview"),
    (Provider.OPENAI, "gpt-4o-mini"),
    (Provider.XAI, "grok-3-mini"),
]

VERTEX_MODELS = [
    (Provider.GOOGLE, "gemini-2.5-flash", "global"),
    (Provider.ANTHROPIC, "claude-haiku-4-5", "us-east5"),
    (Provider.MISTRAL, "mistral-small-2503", "us-central1"),
    (Provider.DEEPSEEK, "deepseek-ai/deepseek-v3.2-maas", "global"),
]


@pytest.mark.parametrize(("provider", "model"), MODELS)
async def test_generate(provider: Provider, model: str) -> None:
    client = create_client(modality=Modality.TEXT, provider=provider, model=model)

    response = await client.generate(prompt="Say hello", max_tokens=200)

    assert isinstance(response, TextOutput)
    assert response.content
    assert isinstance(response.usage, TextUsage)


@pytest.mark.parametrize(("provider", "model"), MODELS)
async def test_stream_generate(provider: Provider, model: str) -> None:
    client = create_client(modality=Modality.TEXT, provider=provider, model=model)

    chunks = [
        chunk
        async for chunk in client.stream.generate(prompt="Say hello", max_tokens=200)
    ]

    assert chunks
    assert all(isinstance(chunk, TextChunk) for chunk in chunks)
    assert any(chunk.content for chunk in chunks)


@pytest.mark.parametrize(("provider", "model", "location"), VERTEX_MODELS)
async def test_vertex_generate(provider: Provider, model: str, location: str) -> None:
    client = create_client(
        modality=Modality.TEXT,
        provider=provider,
        model=model,
        auth=GoogleADC(location=location),
    )

    response = await client.generate(prompt="Say hello", max_tokens=200)

    assert isinstance(response, TextOutput)
    assert response.content


@pytest.mark.parametrize(("provider", "model", "location"), VERTEX_MODELS)
async def test_vertex_stream_generate(
    provider: Provider, model: str, location: str
) -> None:
    client = create_client(
        modality=Modality.TEXT,
        provider=provider,
        model=model,
        auth=GoogleADC(location=location),
    )

    chunks = [
        chunk
        async for chunk in client.stream.generate(prompt="Say hello", max_tokens=200)
    ]

    assert chunks
    assert all(isinstance(chunk, TextChunk) for chunk in chunks)
    assert any(chunk.content for chunk in chunks)
