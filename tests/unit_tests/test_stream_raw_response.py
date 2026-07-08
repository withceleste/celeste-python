"""Streaming reconstructs metadata["raw_response"] so billing reads complete usage."""

from collections.abc import AsyncIterator
from typing import Any

from celeste.modalities.text.protocols.chatcompletions import ChatCompletionsTextStream
from celeste.modalities.text.protocols.openresponses import OpenResponsesTextStream
from celeste.modalities.text.providers.anthropic.client import AnthropicTextStream


async def _async_iter(items: list[dict[str, Any]]) -> AsyncIterator[dict[str, Any]]:
    for item in items:
        yield item


async def test_anthropic_stream_assembles_raw_response_with_complete_usage() -> None:
    events = [
        {
            "type": "message_start",
            "message": {
                "id": "msg_01",
                "model": "claude-sonnet-5",
                "usage": {
                    "input_tokens": 6000,
                    "cache_creation": {"ephemeral_5m_input_tokens": 1200},
                    "cache_read_input_tokens": 40,
                    "server_tool_use": {"web_search_requests": 4},
                },
            },
        },
        {
            "type": "content_block_delta",
            "index": 0,
            "delta": {"type": "text_delta", "text": "done"},
        },
        {
            "type": "message_delta",
            "delta": {"stop_reason": "end_turn"},
            "usage": {"output_tokens": 305},
        },
    ]
    stream = AnthropicTextStream(_async_iter(events))

    async for _ in stream:
        pass

    output = stream.output
    raw_response = output.metadata["raw_response"]
    assert raw_response["id"] == "msg_01"
    assert raw_response["stop_reason"] == "end_turn"
    assert raw_response["usage"] == {
        "input_tokens": 6000,
        "output_tokens": 305,
        "cache_creation": {"ephemeral_5m_input_tokens": 1200},
        "cache_read_input_tokens": 40,
        "server_tool_use": {"web_search_requests": 4},
    }
    # Typed usage is derived from the assembled response, not last-chunk-wins.
    assert output.usage.input_tokens == 6000
    assert output.usage.output_tokens == 305
    assert output.usage.cached_tokens == 40


async def test_openresponses_stream_unwraps_completed_response() -> None:
    response = {
        "id": "resp_01",
        "status": "completed",
        "usage": {"input_tokens": 100, "output_tokens": 20},
        "output": [],
    }
    events = [
        {
            "type": "response.output_text.delta",
            "delta": "done",
            "content_index": 0,
        },
        {"type": "response.completed", "response": response},
    ]
    stream = OpenResponsesTextStream(_async_iter(events))

    async for _ in stream:
        pass

    assert stream.output.metadata["raw_response"] == response
    assert stream.output.usage.input_tokens == 100


async def test_chatcompletions_stream_keeps_terminal_usage_event() -> None:
    final_chunk = {
        "id": "chatcmpl-01",
        "object": "chat.completion.chunk",
        "choices": [],
        "usage": {"prompt_tokens": 50, "completion_tokens": 10, "total_tokens": 60},
    }
    events = [
        {
            "object": "chat.completion.chunk",
            "choices": [{"delta": {"content": "done"}}],
        },
        final_chunk,
    ]
    stream = ChatCompletionsTextStream(_async_iter(events))

    async for _ in stream:
        pass

    assert stream.output.metadata["raw_response"] == final_chunk
    # Typed usage unchanged for single-terminal-event protocols.
    assert stream.output.usage.input_tokens == 50
    assert stream.output.usage.output_tokens == 10
