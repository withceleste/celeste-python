"""Stream termination and HTTP body cleanup."""

import asyncio
from collections.abc import AsyncIterator
from typing import Any

import httpx
import pytest
from pydantic import BaseModel

from celeste.exceptions import StreamEventError, StreamNotExhaustedError

from ._http_helpers import _mock_http, _sse, _text_client


@pytest.mark.parametrize(
    ("status", "typed"),
    [("failed", False), ("incomplete", False), ("incomplete", True)],
)
async def test_responses_terminal_status_is_not_silently_dropped(
    status: str, typed: bool
) -> None:
    class Args(BaseModel):
        value: str

    response: dict[str, Any] = {
        "id": "resp_test",
        "status": status,
        "usage": {"input_tokens": 12, "output_tokens": 5, "total_tokens": 17},
        "error": {"code": "server_error", "message": "provider failure"}
        if status == "failed"
        else None,
        "incomplete_details": {"reason": "max_output_tokens"}
        if status == "incomplete"
        else None,
        "output": [
            {
                "type": "reasoning",
                "id": "reasoning_test",
                "encrypted_content": "signature",
                "summary": [],
            },
            *[
                {
                    "type": "function_call",
                    "call_id": call_status or "omitted",
                    "name": "call",
                    "arguments": '{"value":"ok"}'
                    if call_status != "incomplete"
                    else '{"value":',
                    **({"status": call_status} if call_status else {}),
                }
                for call_status in ("completed", None, "incomplete", "in_progress")
            ],
        ],
    }
    terminal = {"type": f"response.{status}", "response": response}
    async with _mock_http(
        lambda _: _sse(
            {"type": "response.output_text.delta", "delta": "Partial"},
            terminal,
        )
    ):
        stream = _text_client().stream.generate(
            "hello",
            tools=[
                {
                    "name": "call",
                    "parameters": Args if typed else Args.model_json_schema(),
                }
            ],
        )
        assert (await anext(stream)).content == "Partial"
        if status == "failed":
            with pytest.raises(StreamEventError, match="provider failure") as error:
                _ = [chunk async for chunk in stream]
            assert error.value.error_type == "server_error"
            assert error.value.event_data == terminal
            with pytest.raises(StreamNotExhaustedError):
                _ = stream.output
        else:
            _ = [chunk async for chunk in stream]
            assert stream.output.content == "Partial"
            assert stream.output.usage.total_tokens == 17
            assert stream.output.finish_reason is not None
            assert stream.output.finish_reason.reason == "max_output_tokens"
            assert stream.output.metadata["raw_response"] == response
            assert stream.output.signature == response["output"][:1]
            assert [(call.id, call.arguments) for call in stream.output.tool_calls] == [
                ("completed", {"value": "ok"}),
                ("omitted", {"value": "ok"}),
            ]


@pytest.mark.parametrize("mode", ["early", "pending_first", "pending_next", "cancel"])
async def test_stream_close_reaches_http_body_before_returning(mode: str) -> None:
    blocked = asyncio.Event()

    class Body(httpx.AsyncByteStream):
        closed = False

        async def __aiter__(self) -> AsyncIterator[bytes]:
            if mode != "pending_first":
                yield b'data: {"type":"response.output_text.delta","delta":"first"}\n\n'
            blocked.set()
            await asyncio.Event().wait()
            yield b'data: {"type":"response.output_text.delta","delta":"after-close"}\n\n'

        async def aclose(self) -> None:
            self.closed = True

    body = Body()
    async with _mock_http(
        lambda _: httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=body,
        )
    ):
        stream = _text_client().stream.generate("hello")
        if mode != "pending_first":
            assert (await anext(stream)).content == "first"
        if mode == "early":
            await stream.aclose()
        else:
            pending = asyncio.create_task(anext(stream))
            await asyncio.wait_for(blocked.wait(), 2)
            if mode == "cancel":
                pending.cancel()
            else:
                await asyncio.wait_for(stream.aclose(), 2)
            with pytest.raises(asyncio.CancelledError):
                await pending
        assert body.closed
        await stream.aclose()
        with pytest.raises(StopAsyncIteration):
            await anext(stream)
        with pytest.raises(StreamNotExhaustedError):
            _ = stream.output
