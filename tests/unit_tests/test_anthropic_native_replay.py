"""Regression test for Anthropic native assistant transcript replay."""

from collections.abc import AsyncIterator
from typing import Any

from celeste.modalities.text.io import TextInput
from celeste.modalities.text.providers.anthropic.client import AnthropicTextStream
from tests.unit_tests.conftest import anthropic_test_client


async def _async_iter(items: list[dict[str, Any]]) -> AsyncIterator[dict[str, Any]]:
    for item in items:
        yield item


async def test_anthropic_stream_preserves_server_tool_result_for_replay() -> None:
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

    request = anthropic_test_client()._init_request(
        TextInput(messages=[output.message])
    )

    assert request["messages"][0]["content"] == signature


async def test_anthropic_stream_preserves_caller_and_container_for_replay() -> None:
    caller = {"type": "code_execution_20260120", "tool_id": "srvtoolu_01"}
    container = {"id": "container_xyz", "expires_at": "2026-07-08T00:00:00Z"}
    events = [
        {
            "type": "message_start",
            "message": {"id": "msg_01", "container": container},
        },
        {
            "type": "content_block_start",
            "index": 0,
            "content_block": {
                "type": "server_tool_use",
                "id": "srvtoolu_01",
                "name": "code_execution",
            },
        },
        {
            "type": "content_block_delta",
            "index": 0,
            "delta": {
                "type": "input_json_delta",
                "partial_json": '{"code":"rows = await query_database(...)"}',
            },
        },
        {
            "type": "content_block_start",
            "index": 1,
            "content_block": {
                "type": "tool_use",
                "id": "toolu_01",
                "name": "query_database",
                "caller": caller,
            },
        },
        {
            "type": "content_block_delta",
            "index": 1,
            "delta": {"type": "input_json_delta", "partial_json": '{"sql":"SELECT 1"}'},
        },
        {
            "type": "message_delta",
            "delta": {"stop_reason": "tool_use"},
            "usage": {"output_tokens": 10},
        },
    ]
    stream = AnthropicTextStream(_async_iter(events))

    async for _ in stream:
        pass

    output = stream.output
    signature = output.signature
    assert signature is not None
    assert [block["type"] for block in signature] == ["server_tool_use", "tool_use"]
    assert signature[1]["caller"] == caller
    assert output.container == container
    assert [(tc.name, tc.arguments) for tc in output.tool_calls] == [
        ("query_database", {"sql": "SELECT 1"})
    ]

    request = anthropic_test_client()._init_request(
        TextInput(messages=[output.message])
    )

    assert request["messages"][0]["content"] == signature
    assert request["container"] == "container_xyz"


async def test_anthropic_programmatic_tool_use_alone_triggers_native_replay() -> None:
    # Continuation responses carry ONLY the next programmatic tool_use (no
    # server_tool_use/thinking); its caller must still be replayed verbatim.
    caller = {"type": "code_execution_20260120", "tool_id": "srvtoolu_01"}
    events = [
        {
            "type": "content_block_start",
            "index": 0,
            "content_block": {
                "type": "tool_use",
                "id": "toolu_02",
                "name": "query_database",
                "caller": caller,
            },
        },
        {
            "type": "content_block_delta",
            "index": 0,
            "delta": {"type": "input_json_delta", "partial_json": '{"sql":"SELECT 2"}'},
        },
        {
            "type": "message_delta",
            "delta": {"stop_reason": "tool_use"},
            "usage": {"output_tokens": 5},
        },
    ]
    stream = AnthropicTextStream(_async_iter(events))

    async for _ in stream:
        pass

    signature = stream.output.signature
    assert signature is not None and signature[0]["caller"] == caller
