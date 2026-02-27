"""Integration tests for tools= parameter - WebSearch, function tools, streaming."""

import warnings

# Suppress deprecation warnings from legacy capability packages
warnings.filterwarnings(
    "ignore",
    message=".*capability parameter is deprecated.*",
    category=DeprecationWarning,
)

import pytest  # noqa: E402

from celeste import Modality, create_client  # noqa: E402
from celeste.modalities.text import TextChunk, TextOutput  # noqa: E402
from celeste.tools import ToolResult, WebSearch, XSearch  # noqa: E402
from celeste.types import Message, Role  # noqa: E402

# One cheap model per provider for server-side tools (WebSearch/XSearch)
# xAI: only grok-4+ supports server-side tools
SERVER_TOOL_MODELS = [
    ("anthropic", "claude-haiku-4-5"),
    ("openai", "gpt-4o-mini"),
    ("google", "gemini-2.5-flash"),
    ("xai", "grok-4-fast-non-reasoning"),
]

# One cheap model per provider for function tools (user-defined)
FUNCTION_TOOL_MODELS = [
    ("anthropic", "claude-haiku-4-5"),
    ("openai", "gpt-4o-mini"),
    ("google", "gemini-2.5-flash"),
    ("xai", "grok-3-mini"),
]

WEATHER_TOOL = {
    "name": "get_weather",
    "description": "Get current weather for a city. You MUST call this tool.",
    "parameters": {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"],
    },
}

TEST_MAX_TOKENS = 500


# -- WebSearch (non-streaming) --


@pytest.mark.parametrize(
    ("provider", "model_id"),
    SERVER_TOOL_MODELS,
    ids=[f"{p}-{m}" for p, m in SERVER_TOOL_MODELS],
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_web_search(provider: str, model_id: str) -> None:
    """Test WebSearch tool produces a text response across all providers."""
    client = create_client(modality=Modality.TEXT, provider=provider, model=model_id)

    output = await client.generate(
        prompt="What year was Python 3.12 released?",
        tools=[WebSearch()],
        max_tokens=TEST_MAX_TOKENS,
    )

    assert isinstance(output, TextOutput)
    assert output.content


# -- WebSearch (streaming) --


@pytest.mark.parametrize(
    ("provider", "model_id"),
    SERVER_TOOL_MODELS,
    ids=[f"{p}-{m}" for p, m in SERVER_TOOL_MODELS],
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_stream_web_search(provider: str, model_id: str) -> None:
    """Test streaming with WebSearch tool across all providers."""
    client = create_client(modality=Modality.TEXT, provider=provider, model=model_id)

    chunks: list[TextChunk] = []
    async for chunk in client.stream.generate(
        prompt="What year was Python 3.12 released?",
        tools=[WebSearch()],
        max_tokens=TEST_MAX_TOKENS,
    ):
        chunks.append(chunk)

    assert chunks
    assert all(isinstance(c, TextChunk) for c in chunks)


# -- User-defined function tool -> ToolCall parsing --


@pytest.mark.parametrize(
    ("provider", "model_id"),
    FUNCTION_TOOL_MODELS,
    ids=[f"{p}-{m}" for p, m in FUNCTION_TOOL_MODELS],
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_function_tool_call(provider: str, model_id: str) -> None:
    """Test user-defined function tool returns parsed ToolCall objects."""
    client = create_client(modality=Modality.TEXT, provider=provider, model=model_id)

    output = await client.generate(
        prompt="What is the weather in Paris right now? Use the get_weather tool.",
        tools=[WEATHER_TOOL],
        max_tokens=TEST_MAX_TOKENS,
    )

    assert isinstance(output, TextOutput)
    assert len(output.tool_calls) > 0, (
        f"{provider}/{model_id} did not return tool_calls"
    )
    tc = output.tool_calls[0]
    assert tc.name == "get_weather"
    assert "city" in tc.arguments


# -- xAI-specific: XSearch --


@pytest.mark.integration
@pytest.mark.asyncio
async def test_xai_x_search() -> None:
    """Test XSearch tool (xAI-only) produces a text response."""
    client = create_client(
        modality=Modality.TEXT, provider="xai", model="grok-4-fast-non-reasoning"
    )

    output = await client.generate(
        prompt="What is trending on X right now?",
        tools=[XSearch()],
        max_tokens=TEST_MAX_TOKENS,
    )

    assert isinstance(output, TextOutput)
    assert output.content


# -- Multi-turn ToolResult round-trip --


@pytest.mark.parametrize(
    ("provider", "model_id"),
    FUNCTION_TOOL_MODELS,
    ids=[f"{p}-{m}" for p, m in FUNCTION_TOOL_MODELS],
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_tool_result_round_trip(provider: str, model_id: str) -> None:
    """Test full round-trip: tool call -> tool result -> final answer."""
    client = create_client(modality=Modality.TEXT, provider=provider, model=model_id)

    # Step 1: Get tool call
    output1 = await client.generate(
        prompt="What is the weather in Paris right now? Use the get_weather tool.",
        tools=[WEATHER_TOOL],
        max_tokens=TEST_MAX_TOKENS,
    )

    assert output1.tool_calls, f"{provider}/{model_id} did not return tool_calls"
    tc = output1.tool_calls[0]
    assert tc.name == "get_weather"

    # Step 2: Send tool result back using output.message for round-trip
    output2 = await client.generate(
        messages=[
            Message(
                role=Role.USER,
                content="What is the weather in Paris right now? Use the get_weather tool.",
            ),
            output1.message,
            ToolResult(content="18°C, sunny", tool_call_id=tc.id, name=tc.name),
        ],
        tools=[WEATHER_TOOL],
        max_tokens=TEST_MAX_TOKENS,
    )

    assert isinstance(output2, TextOutput)
    assert output2.content, f"{provider}/{model_id} did not return final text answer"
