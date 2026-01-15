"""Unit tests for streaming metadata built from provider response_data."""

from collections.abc import AsyncIterator
from typing import Any

from pydantic import SecretStr

from celeste import Model
from celeste.auth import AuthHeader
from celeste.core import Modality, Operation, Provider
from celeste.modalities.text.providers.google.client import (
    GoogleTextClient,
    GoogleTextStream,
)
from celeste.modalities.text.providers.openai.client import (
    OpenAITextClient,
    OpenAITextStream,
)


async def _async_iter(items: list[dict[str, Any]]) -> AsyncIterator[dict[str, Any]]:
    for item in items:
        yield item


async def test_openai_stream_builds_metadata_from_inner_response_data() -> None:
    model = Model(
        id="gpt-4o-mini",
        provider=Provider.OPENAI,
        display_name="GPT-4o mini",
        operations={Modality.TEXT: {Operation.GENERATE}},
    )
    client = OpenAITextClient(
        model=model,
        provider=Provider.OPENAI,
        auth=AuthHeader(secret=SecretStr("test")),
    )

    response_data = {
        "status": "completed",
        "output": [
            {"type": "message", "content": [{"type": "output_text", "text": "x"}]}
        ],
        "usage": {"input_tokens": 1, "output_tokens": 2, "total_tokens": 3},
    }

    events: list[dict[str, Any]] = [
        {"type": "response.output_text.delta", "delta": "Hello"},
        {"type": "response.completed", "response": response_data},
    ]

    stream = OpenAITextStream(
        _async_iter(events),
        transform_output=lambda x, **_: x,
        client=client,
        **{},
    )

    async for _ in stream:
        pass

    metadata = stream.output.metadata
    raw_events = metadata.get("raw_events", [])
    assert len(raw_events) == 1  # Only response_data, deltas filtered
    assert raw_events[0].get("status") == "completed"


async def test_google_stream_builds_metadata_from_event_response_data() -> None:
    model = Model(
        id="gemini-2.5-pro",
        provider=Provider.GOOGLE,
        display_name="Gemini 2.5 Pro",
        operations={Modality.TEXT: {Operation.GENERATE}},
    )
    client = GoogleTextClient(
        model=model,
        provider=Provider.GOOGLE,
        auth=AuthHeader(secret=SecretStr("test"), header="x-goog-api-key", prefix=""),
    )

    event = {
        "candidates": [
            {
                "content": {"parts": [{"text": "Hello"}]},
                "finishReason": "STOP",
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 1,
            "candidatesTokenCount": 2,
            "totalTokenCount": 3,
        },
    }

    stream = GoogleTextStream(
        _async_iter([event]),
        transform_output=lambda x, **_: x,
        client=client,
        **{},
    )

    async for _ in stream:
        pass

    metadata = stream.output.metadata
    raw_events = metadata.get("raw_events", [])
    assert len(raw_events) == 1
    assert raw_events[0].get("usageMetadata", {}).get("totalTokenCount") == 3


async def test_openai_stream_filters_content_only_events() -> None:
    """Test that content-only delta events are filtered from raw_events."""
    model = Model(
        id="gpt-4o-mini",
        provider=Provider.OPENAI,
        display_name="GPT-4o mini",
        operations={Modality.TEXT: {Operation.GENERATE}},
    )
    client = OpenAITextClient(
        model=model,
        provider=Provider.OPENAI,
        auth=AuthHeader(secret=SecretStr("test")),
    )

    response_data = {
        "status": "completed",
        "usage": {"input_tokens": 1, "output_tokens": 2, "total_tokens": 3},
    }

    # Include multiple content-only delta events - these should be filtered
    events: list[dict[str, Any]] = [
        {"type": "response.output_text.delta", "delta": "Hello"},
        {"type": "response.output_text.delta", "delta": " world"},
        {"type": "response.output_text.delta", "delta": "!"},
        {"type": "response.completed", "response": response_data},
    ]

    stream = OpenAITextStream(
        _async_iter(events),
        transform_output=lambda x, **_: x,
        client=client,
        **{},
    )

    async for _ in stream:
        pass

    raw_events = stream.output.metadata.get("raw_events", [])
    # Only the initial response should remain (delta events filtered)
    event_types = [e.get("type") for e in raw_events]
    assert "response.output_text.delta" not in event_types


async def test_openai_stream_aggregates_usage_from_last_event() -> None:
    """Test that usage is taken from the last event with usage data."""
    model = Model(
        id="gpt-4o-mini",
        provider=Provider.OPENAI,
        display_name="GPT-4o mini",
        operations={Modality.TEXT: {Operation.GENERATE}},
    )
    client = OpenAITextClient(
        model=model,
        provider=Provider.OPENAI,
        auth=AuthHeader(secret=SecretStr("test")),
    )

    # Simulate multiple events with usage (last one should win)
    events: list[dict[str, Any]] = [
        {"type": "response.output_text.delta", "delta": "Hello"},
        {
            "type": "response.completed",
            "response": {
                "status": "completed",
                "usage": {"input_tokens": 10, "output_tokens": 20, "total_tokens": 30},
            },
        },
    ]

    stream = OpenAITextStream(
        _async_iter(events),
        transform_output=lambda x, **_: x,
        client=client,
        **{},
    )

    async for _ in stream:
        pass

    # Usage should be from the completed event
    usage = stream.output.usage
    assert usage.input_tokens == 10
    assert usage.output_tokens == 20
    assert usage.total_tokens == 30
