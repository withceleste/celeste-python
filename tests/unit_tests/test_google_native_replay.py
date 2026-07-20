"""Regression coverage for Google native tool transcript replay."""

from collections.abc import AsyncIterator
from typing import Any

from pydantic import SecretStr

from celeste import Model
from celeste.auth import AuthHeader
from celeste.core import Provider
from celeste.modalities.text.io import TextInput
from celeste.modalities.text.providers.google.vertex import (
    GoogleVertexTextClient,
    GoogleVertexTextStream,
)
from celeste.tools import ToolResult


async def _async_iter(items: list[dict[str, Any]]) -> AsyncIterator[dict[str, Any]]:
    for item in items:
        yield item


async def test_google_stream_replays_native_tool_parts_verbatim() -> None:
    parts = [
        {
            "toolCall": {
                "toolType": "GOOGLE_SEARCH_WEB",
                "args": {"queries": ["today's news"]},
                "id": "search-1",
            },
            "thoughtSignature": "search-call-signature",
        },
        {
            "toolResponse": {
                "toolType": "GOOGLE_SEARCH_WEB",
                "response": {"search_suggestions": "<div>suggestions</div>"},
                "id": "search-1",
            },
            "thoughtSignature": "search-response-signature",
        },
        {
            "functionCall": {
                "name": "generate_audio",
                "args": {"text": "news"},
                "id": "audio-1",
            },
            "thoughtSignature": "audio-call-signature",
        },
    ]
    events: list[dict[str, Any]] = [
        {"candidates": [{"content": {"parts": [part]}}]} for part in parts
    ]
    events[-1]["candidates"][0]["finishReason"] = "STOP"
    events[-1]["usageMetadata"] = {"totalTokenCount": 3}

    stream = GoogleVertexTextStream(_async_iter(events))
    async for _ in stream:
        pass

    output = stream.output
    assert output.signature == parts
    assert output.tool_calls[0].id == "audio-1"

    client = GoogleVertexTextClient(
        model=Model(
            id="test-model", provider=Provider.GOOGLE, display_name="Test Model"
        ),
        provider=Provider.GOOGLE,
        auth=AuthHeader(secret=SecretStr("test")),
    )
    request = client._init_request(
        TextInput(
            messages=[
                output.message,
                ToolResult(
                    tool_call_id="audio-1",
                    name="generate_audio",
                    content="audio-artifact-1",
                ),
            ]
        )
    )

    assert request["contents"][0] == {"role": "model", "parts": parts}
    assert request["contents"][1]["parts"][0]["functionResponse"]["id"] == "audio-1"
