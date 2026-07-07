"""Regression test for Anthropic native assistant transcript replay."""

from collections.abc import AsyncIterator
from typing import Any

from pydantic import SecretStr

from celeste import Model
from celeste.auth import AuthHeader
from celeste.core import Modality, Operation, Provider
from celeste.modalities.text.io import TextInput
from celeste.modalities.text.providers.anthropic.client import (
    AnthropicTextClient,
    AnthropicTextStream,
)


async def _async_iter(items: list[dict[str, Any]]) -> AsyncIterator[dict[str, Any]]:
    for item in items:
        yield item


async def test_anthropic_stream_preserves_server_tool_result_for_replay() -> None:
    model = Model(
        id="claude-sonnet-5",
        provider=Provider.ANTHROPIC,
        display_name="Claude Sonnet 5",
        operations={Modality.TEXT: {Operation.GENERATE}},
    )
    events = [
        {
            "type": "content_block_start",
            "index": 0,
            "content_block": {
                "type": "server_tool_use",
                "id": "srvtoolu_01",
                "name": "bash_code_execution",
            },
        },
        {
            "type": "content_block_delta",
            "index": 0,
            "delta": {
                "type": "input_json_delta",
                "partial_json": '{"code":"print(1)"}',
            },
        },
        {
            "type": "content_block_start",
            "index": 1,
            "content_block": {
                "type": "bash_code_execution_tool_result",
                "tool_use_id": "srvtoolu_01",
                "content": [{"type": "text", "text": "1\n"}],
            },
        },
        {
            "type": "content_block_delta",
            "index": 2,
            "delta": {"type": "text_delta", "text": "done"},
        },
    ]
    stream = AnthropicTextStream(_async_iter(events))

    async for _ in stream:
        pass

    output = stream.output
    signature = output.signature
    assert signature is not None
    assert [block["type"] for block in signature] == [
        "server_tool_use",
        "bash_code_execution_tool_result",
        "text",
    ]
    assert output.tool_calls == []

    client = AnthropicTextClient(
        model=model,
        provider=Provider.ANTHROPIC,
        auth=AuthHeader(secret=SecretStr("test"), header="x-api-key", prefix=""),
    )
    request = client._init_request(TextInput(messages=[output.message]))

    assert request["messages"][0]["content"] == signature
