"""Unit tests for streaming metadata built from provider response_data."""

from collections.abc import AsyncIterator
from typing import Any

from celeste.core import Modality, Provider
from celeste.modalities.text.providers.google.interactions import (
    GoogleInteractionsTextStream,
)
from celeste.modalities.text.providers.google.vertex import GoogleVertexTextStream
from celeste.modalities.text.providers.openai.client import OpenAITextStream


async def _async_iter(items: list[dict[str, Any]]) -> AsyncIterator[dict[str, Any]]:
    for item in items:
        yield item


async def test_openai_stream_builds_metadata_from_inner_response_data() -> None:
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
        stream_metadata={
            "model": "gpt-4o-mini",
            "provider": Provider.OPENAI,
            "modality": Modality.TEXT,
        },
        **{},
    )

    async for _ in stream:
        pass

    metadata = stream.output.metadata
    raw_events = metadata.get("raw_events", [])
    assert len(raw_events) == 1  # Only response_data, deltas filtered
    assert raw_events[0].get("status") == "completed"


async def test_google_stream_builds_metadata_from_event_response_data() -> None:
    """GoogleInteractionsTextStream (Interactions API, default for API-key auth)."""
    event = {
        "event_type": "interaction.completed",
        "interaction": {
            "status": "completed",
            "steps": [
                {
                    "type": "model_output",
                    "content": [{"type": "text", "text": "Hello"}],
                }
            ],
            "usage": {
                "total_input_tokens": 1,
                "total_output_tokens": 2,
                "total_tokens": 3,
            },
        },
    }

    stream = GoogleInteractionsTextStream(
        _async_iter([event]),
        transform_output=lambda x, **_: x,
        stream_metadata={
            "model": "gemini-2.5-pro",
            "provider": Provider.GOOGLE,
            "modality": Modality.TEXT,
        },
        **{},
    )

    async for _ in stream:
        pass

    metadata = stream.output.metadata
    raw_events = metadata.get("raw_events", [])
    assert len(raw_events) == 1
    assert raw_events[0]["interaction"]["usage"]["total_tokens"] == 3


async def test_google_vertex_stream_builds_metadata_from_event_response_data() -> None:
    """GoogleVertexTextStream (GenerateContent API, used only for GoogleADC auth)."""
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

    stream = GoogleVertexTextStream(
        _async_iter([event]),
        transform_output=lambda x, **_: x,
        stream_metadata={
            "model": "gemini-2.5-pro",
            "provider": Provider.GOOGLE,
            "modality": Modality.TEXT,
        },
        **{},
    )

    async for _ in stream:
        pass

    metadata = stream.output.metadata
    raw_events = metadata.get("raw_events", [])
    assert len(raw_events) == 1
    assert raw_events[0].get("usageMetadata", {}).get("totalTokenCount") == 3
