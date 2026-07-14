import pytest

from celeste import Modality, Provider, create_client
from celeste.modalities.text import TextOutput, TextUsage

CASES = [
    (Provider.ANTHROPIC, "claude-haiku-4-5", "square_image", "image"),
    (Provider.COHERE, "command-a-vision-07-2025", "square_image", "image"),
    (Provider.GOOGLE, "gemini-2.5-flash-lite", "square_image", "image"),
    (
        Provider.GROQ,
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "square_image",
        "image",
    ),
    (Provider.HUGGINGFACE, "google/gemma-3n-E4B-it", "square_image", "image"),
    (Provider.MISTRAL, "pixtral-12b-latest", "square_image", "image"),
    (
        Provider.MOONSHOT,
        "moonshot-v1-8k-vision-preview",
        "square_image",
        "image",
    ),
    (Provider.OPENAI, "gpt-4o-mini", "square_image", "image"),
    (
        Provider.XAI,
        "grok-4.20-0309-non-reasoning",
        "square_image",
        "image",
    ),
    (Provider.ANTHROPIC, "claude-haiku-4-5", "test_document", "document"),
    (Provider.GOOGLE, "gemini-2.5-flash-lite", "test_document", "document"),
    (Provider.MISTRAL, "pixtral-12b-latest", "test_document", "document"),
    (Provider.OPENAI, "gpt-4o-mini", "test_document", "document"),
    (Provider.GOOGLE, "gemini-2.5-flash-lite", "test_audio", "audio"),
    (Provider.GOOGLE, "gemini-2.5-flash-lite", "test_video", "video"),
]


@pytest.mark.parametrize(("provider", "model", "fixture", "media_name"), CASES)
async def test_analyze(
    provider: Provider,
    model: str,
    fixture: str,
    media_name: str,
    request: pytest.FixtureRequest,
) -> None:
    client = create_client(modality=Modality.TEXT, provider=provider, model=model)

    response = await client.analyze(
        prompt="Describe this",
        max_tokens=200,
        **{media_name: request.getfixturevalue(fixture)},
    )

    assert isinstance(response, TextOutput)
    assert response.content
    assert isinstance(response.usage, TextUsage)
