import pytest

from celeste import Modality, Provider, ToolChoice, create_client
from celeste.modalities.text import TextChunk, TextOutput
from celeste.tools import WebSearch, XSearch

WEB_SEARCH_MODELS = [
    (Provider.ANTHROPIC, "claude-haiku-4-5"),
    (Provider.GOOGLE, "gemini-2.5-flash-lite"),
    (Provider.GROQ, "openai/gpt-oss-20b"),
    (Provider.MOONSHOT, "kimi-k2-0711-preview"),
    (Provider.OPENAI, "gpt-4o-mini"),
    (Provider.XAI, "grok-4.20-0309-non-reasoning"),
]

FUNCTION_TOOL_MODELS = [
    (Provider.ANTHROPIC, "claude-haiku-4-5", True),
    (Provider.DEEPSEEK, "deepseek-chat", True),
    (Provider.GOOGLE, "gemini-2.5-flash-lite", True),
    (Provider.GROQ, "llama-3.1-8b-instant", False),
    (Provider.HUGGINGFACE, "Qwen/Qwen3-4B-Instruct-2507", False),
    (Provider.MISTRAL, "mistral-tiny", True),
    (Provider.MOONSHOT, "kimi-k2-0711-preview", True),
    (Provider.OPENAI, "gpt-4o-mini", True),
    (Provider.XAI, "grok-3-mini", False),
]

WEATHER_TOOL = {
    "name": "get_weather",
    "description": "Get current weather for a city. You must call this tool.",
    "parameters": {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"],
    },
}


@pytest.mark.parametrize(("provider", "model"), WEB_SEARCH_MODELS)
async def test_web_search(provider: Provider, model: str) -> None:
    client = create_client(modality=Modality.TEXT, provider=provider, model=model)

    output = await client.generate(
        prompt="When was Python 3.12 released?", tools=[WebSearch()], max_tokens=500
    )

    assert isinstance(output, TextOutput)
    assert output.content


@pytest.mark.parametrize(("provider", "model"), WEB_SEARCH_MODELS)
async def test_stream_web_search(provider: Provider, model: str) -> None:
    client = create_client(modality=Modality.TEXT, provider=provider, model=model)

    chunks = [
        chunk
        async for chunk in client.stream.generate(
            prompt="When was Python 3.12 released?",
            tools=[WebSearch()],
            max_tokens=500,
        )
    ]

    assert chunks
    assert all(isinstance(chunk, TextChunk) for chunk in chunks)


@pytest.mark.parametrize(
    ("provider", "model", "supports_required"), FUNCTION_TOOL_MODELS
)
async def test_function_tool_call(
    provider: Provider, model: str, supports_required: bool
) -> None:
    client = create_client(modality=Modality.TEXT, provider=provider, model=model)
    parameters = {"tool_choice": ToolChoice.REQUIRED} if supports_required else {}

    output = await client.generate(
        prompt="Use get_weather to check the weather in Paris.",
        tools=[WEATHER_TOOL],
        max_tokens=500,
        **parameters,
    )

    assert isinstance(output, TextOutput)
    assert output.tool_calls
    assert output.tool_calls[0].name == "get_weather"
    assert "city" in output.tool_calls[0].arguments


async def test_x_search() -> None:
    client = create_client(
        modality=Modality.TEXT,
        provider=Provider.XAI,
        model="grok-4.20-0309-non-reasoning",
    )

    output = await client.generate(
        prompt="What is trending on X?", tools=[XSearch()], max_tokens=500
    )

    assert isinstance(output, TextOutput)
    assert output.content
