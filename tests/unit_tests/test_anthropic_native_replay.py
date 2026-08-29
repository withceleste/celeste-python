"""Regression test for Anthropic native assistant transcript replay."""

from collections.abc import AsyncIterator
from typing import Any

import pytest
from pydantic import BaseModel

from celeste.core import Provider
from celeste.exceptions import StreamEventError
from celeste.modalities.text.io import TextInput
from celeste.modalities.text.providers.anthropic.client import AnthropicTextStream
from tests.unit_tests.conftest import anthropic_test_client


class _RefusalSchema(BaseModel):
    value: int


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


async def test_anthropic_stream_preserves_valid_blocks_across_fallback() -> None:
    fallback = {
        "type": "fallback",
        "from": {"model": "claude-opus-5"},
        "to": {"model": "claude-opus-4-8"},
    }
    events = [
        {
            "type": "message_start",
            "message": {
                "id": "msg_01",
                "model": "claude-opus-5",
                "usage": {"input_tokens": 10},
            },
        },
        {
            "type": "content_block_delta",
            "index": 0,
            "delta": {"type": "text_delta", "text": "partial"},
        },
        {
            "type": "content_block_start",
            "index": 1,
            "content_block": {"type": "connector_text", "text": ""},
        },
        {
            "type": "content_block_delta",
            "index": 1,
            "delta": {"type": "text_delta", "text": "tool narration"},
        },
        {
            "type": "content_block_start",
            "index": 2,
            "content_block": fallback,
        },
        {
            "type": "content_block_start",
            "index": 3,
            "content_block": {"type": "thinking", "thinking": ""},
        },
        {
            "type": "content_block_delta",
            "index": 3,
            "delta": {"type": "thinking_delta", "thinking": "new thought"},
        },
        {
            "type": "content_block_delta",
            "index": 4,
            "delta": {"type": "text_delta", "text": "answer"},
        },
        {
            "type": "content_block_start",
            "index": 5,
            "content_block": {
                "type": "connector_text",
                "text": "",
                "signature": "opaque",
            },
        },
        {
            "type": "content_block_delta",
            "index": 5,
            "delta": {"type": "text_delta", "text": "connector narration"},
        },
        {
            "type": "message_delta",
            "delta": {"stop_reason": "end_turn"},
            "usage": {"output_tokens": 12},
        },
    ]
    stream = AnthropicTextStream(_async_iter(events))

    async for _ in stream:
        pass

    signature = stream.output.signature
    assert signature == [
        {"type": "text", "text": "partial"},
        fallback,
        {"type": "thinking", "thinking": "new thought", "signature": ""},
        {"type": "text", "text": "answer"},
        {
            "type": "connector_text",
            "text": "connector narration",
            "signature": "opaque",
        },
    ]
    request = anthropic_test_client()._init_request(
        TextInput(messages=[stream.output.message])
    )
    assert request["messages"][0]["content"] == signature
    assert stream.output.metadata["response_model"] == "claude-opus-4-8"
    assert stream.output.metadata["raw_response"]["model"] == "claude-opus-4-8"


async def test_anthropic_stream_preserves_compaction_for_replay() -> None:
    compaction = {
        "type": "compaction",
        "content": "compacted conversation",
        "encrypted_content": "opaque",
    }
    events = [
        {
            "type": "content_block_start",
            "index": 0,
            "content_block": {"type": "compaction", "content": None},
        },
        {
            "type": "content_block_delta",
            "index": 0,
            "delta": {
                "type": "compaction_delta",
                "content": compaction["content"],
                "encrypted_content": compaction["encrypted_content"],
            },
        },
        {
            "type": "content_block_delta",
            "index": 1,
            "delta": {"type": "text_delta", "text": "continued"},
        },
    ]
    stream = AnthropicTextStream(_async_iter(events))

    async for _ in stream:
        pass

    assert stream.output.signature == [
        compaction,
        {"type": "text", "text": "continued"},
    ]
    request = anthropic_test_client()._init_request(
        TextInput(messages=[stream.output.message])
    )
    assert request["messages"][0]["content"] == stream.output.signature


async def test_anthropic_stream_preserves_mcp_tool_pair_for_replay() -> None:
    tool_use = {
        "type": "mcp_tool_use",
        "id": "mcptoolu_01",
        "name": "search",
        "server_name": "docs",
        "input": {"query": "Opus 5"},
    }
    result = {
        "type": "mcp_tool_result",
        "tool_use_id": "mcptoolu_01",
        "content": [{"type": "text", "text": "found"}],
        "is_error": False,
    }
    events = [
        {
            "type": "content_block_start",
            "index": 0,
            "content_block": {**tool_use, "input": {}},
        },
        {
            "type": "content_block_delta",
            "index": 0,
            "delta": {
                "type": "input_json_delta",
                "partial_json": '{"query":"Opus 5"}',
            },
        },
        {
            "type": "content_block_start",
            "index": 1,
            "content_block": result,
        },
        {
            "type": "message_delta",
            "delta": {"stop_reason": "end_turn"},
            "usage": {"output_tokens": 5},
        },
    ]
    stream = AnthropicTextStream(_async_iter(events))

    async for _ in stream:
        pass

    assert stream.output.signature == [tool_use, result]
    request = anthropic_test_client()._init_request(
        TextInput(messages=[stream.output.message])
    )
    assert request["messages"][0]["content"] == [tool_use, result]


async def test_anthropic_stream_raises_for_vertex_prompt_block() -> None:
    event = {"promptFeedback": {"blockReason": "PROHIBITED_CONTENT"}}
    stream = AnthropicTextStream(
        _async_iter([event]), stream_metadata={"provider": Provider.ANTHROPIC}
    )

    with pytest.raises(StreamEventError, match="PROHIBITED_CONTENT") as caught:
        async for _ in stream:
            pass

    assert caught.value.error_type == "PROHIBITED_CONTENT"


def test_anthropic_pre_output_refusal_is_a_valid_empty_response() -> None:
    client = anthropic_test_client()
    response = {
        "content": [],
        "stop_reason": "refusal",
        "stop_details": {"type": "refusal", "category": "cyber"},
        "usage": {"input_tokens": 10, "output_tokens": 0},
    }

    content = client._parse_content(response)
    assert content == ""
    assert client._transform_output(content, output_schema=_RefusalSchema) == ""
    assert client._parse_usage(response)["output_tokens"] == 0


def test_anthropic_unary_response_joins_all_text_blocks() -> None:
    response = {
        "content": [
            {"type": "text", "text": "first"},
            {"type": "connector_text", "text": " narration"},
            {"type": "fallback", "to": {"model": "claude-opus-4-8"}},
            {"type": "text", "text": " second"},
        ]
    }

    assert anthropic_test_client()._parse_content(response) == "first narration second"
