"""Regression test for Anthropic native assistant transcript replay."""

import json
from collections.abc import AsyncIterator
from typing import Any

import pytest

from celeste.exceptions import StreamNotExhaustedError, ValidationError
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


def _tool_input_events(
    block_type: str, input_data: object, fragments: list[str]
) -> list[dict[str, Any]]:
    return [
        {
            "type": "content_block_start",
            "index": 0,
            "content_block": {
                "type": block_type,
                "id": "toolu_01",
                "name": "query_database",
                **({"input": input_data} if input_data is not Ellipsis else {}),
            },
        },
        *[
            {
                "type": "content_block_delta",
                "index": 0,
                "delta": {"type": "input_json_delta", "partial_json": fragment},
            }
            for fragment in fragments
        ],
        {"type": "content_block_stop", "index": 0},
        {
            "type": "message_delta",
            "delta": {"stop_reason": "tool_use"},
            "usage": {"output_tokens": 5},
        },
    ]


@pytest.mark.parametrize("block_type", ["tool_use", "server_tool_use"])
@pytest.mark.parametrize("arguments", ['{"sql":', "   ", "[]"])
async def test_malformed_anthropic_tool_inputs_do_not_become_empty_replay(
    block_type: str, arguments: str
) -> None:
    stream = AnthropicTextStream(
        _async_iter(_tool_input_events(block_type, {}, [arguments]))
    )
    with pytest.raises(ValidationError, match="query_database") as error:
        _ = [chunk async for chunk in stream]
    if arguments != "[]":
        assert isinstance(error.value.__cause__, json.JSONDecodeError)
    with pytest.raises(StopAsyncIteration):
        await anext(stream)
    with pytest.raises(StreamNotExhaustedError):
        _ = stream.output


@pytest.mark.parametrize("block_type", ["tool_use", "server_tool_use"])
@pytest.mark.parametrize(
    ("input_data", "fragments", "expected"),
    [
        ({}, [], {}),
        (Ellipsis, [], {}),
        ({"sql": "SELECT 1"}, [], {"sql": "SELECT 1"}),
        ({}, ["{", "}"], {}),
    ],
    ids=["native-empty", "native-missing", "native-object", "fragmented-empty"],
)
async def test_valid_anthropic_tool_inputs_survive_native_and_streamed_forms(
    block_type: str,
    input_data: object,
    fragments: list[str],
    expected: dict[str, Any],
) -> None:
    stream = AnthropicTextStream(
        _async_iter(_tool_input_events(block_type, input_data, fragments))
    )
    _ = [chunk async for chunk in stream]
    if block_type == "tool_use":
        assert [call.arguments for call in stream.output.tool_calls] == [expected]
    else:
        assert stream.output.tool_calls == []
        assert stream.output.signature is not None
        assert stream.output.signature[0]["input"] == expected


@pytest.mark.parametrize("block_type", ["tool_use", "server_tool_use"])
@pytest.mark.parametrize(
    "input_data",
    [None, [], '{"sql":', "null"],
    ids=["null", "array", "malformed-json", "json-null"],
)
async def test_invalid_native_tool_inputs_do_not_become_empty_arguments(
    block_type: str, input_data: object
) -> None:
    stream = AnthropicTextStream(
        _async_iter(_tool_input_events(block_type, input_data, []))
    )
    with pytest.raises(ValidationError, match="query_database"):
        _ = [chunk async for chunk in stream]
    with pytest.raises(StopAsyncIteration):
        await anext(stream)
    with pytest.raises(StreamNotExhaustedError):
        _ = stream.output
