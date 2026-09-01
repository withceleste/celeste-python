"""Regression coverage for Google native tool transcript replay."""

from collections.abc import AsyncIterator
from typing import Any

import pytest
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


@pytest.mark.parametrize("bundled", [False, True])
async def test_google_vertex_preserves_all_text_parts(bundled: bool) -> None:
    parts = [
        {"text": "private thought", "thought": True, "thoughtSignature": "sig"},
        {"text": "Let me calculate. "},
        {"executableCode": {"language": "PYTHON", "code": "print(2 + 2)"}},
        {"codeExecutionResult": {"outcome": "OUTCOME_OK", "output": "4\n"}},
        {"text": "The answer is 4."},
    ]
    other_candidate = {"content": {"parts": [{"text": "ignore alternative"}]}}
    response = {
        "candidates": [{"content": {"parts": parts}}, other_candidate],
    }
    client = object.__new__(GoogleVertexTextClient)
    expected = "Let me calculate. The answer is 4."
    assert client._parse_content(response) == expected
    assert client._parse_reasoning(response) == ("private thought", parts)

    groups = [parts] if bundled else [[part] for part in parts]
    events: list[dict[str, Any]] = [
        {"candidates": [{"content": {"parts": group}}, other_candidate]}
        for group in groups
    ]
    events.append({"candidates": [{"finishReason": "STOP"}]})
    stream = GoogleVertexTextStream(_async_iter(events))
    chunks = [chunk async for chunk in stream]
    assert "".join(chunk.content for chunk in chunks) == expected
    assert stream.output.content == expected
    assert stream.output.reasoning == "private thought"
    assert stream.output.signature == parts


def test_google_vertex_non_text_parts_do_not_emit_text() -> None:
    stream = object.__new__(GoogleVertexTextStream)
    for parts in ([], [{"thought": True, "text": "private"}], [{"text": None}]):
        response = {"candidates": [{"content": {"parts": parts}}]}
        assert object.__new__(GoogleVertexTextClient)._parse_content(response) == ""
        assert stream._parse_chunk_content(response) is None
    assert stream._parse_chunk_content({}) is None
