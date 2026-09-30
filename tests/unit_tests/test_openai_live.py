"""OpenAI Live request building, event parsing, and WebSocket transport."""

import asyncio
import base64
import json
from collections.abc import AsyncIterator, Callable
from contextlib import AbstractContextManager, asynccontextmanager
from typing import Any
from unittest.mock import patch

import pytest

import celeste
from celeste import (
    Message,
    Modality,
    Operation,
    Provider,
    Role,
    ToolResult,
    create_client,
)
from celeste.artifacts import AudioArtifact
from celeste.auth import NoAuth
from celeste.exceptions import (
    ConstraintViolationError,
    StreamEventError,
    UnsupportedParameterWarning,
)
from celeste.mime_types import AudioMimeType
from celeste.modalities.live.client import LiveClient
from celeste.modalities.live.io import LiveInput
from celeste.modalities.live.providers.openai.client import OpenAILiveStream
from celeste.modalities.live.providers.openai.models import OPENAI_AUDIO_FORMATS
from celeste.tools import WebSearch


def client() -> LiveClient:
    result = create_client(modality=Modality.LIVE, model="gpt-live-1", auth=NoAuth())
    assert isinstance(result, LiveClient)
    return result


class WebSocket:
    """Scripted server: each client event may queue server events in reply."""

    def __init__(self, reply: Callable[[dict[str, Any]], list[dict[str, Any]]]) -> None:
        self.reply = reply
        self.incoming: asyncio.Queue[dict[str, Any] | None] = asyncio.Queue()
        self.sent: list[dict[str, Any]] = []
        self.closed = False

    async def send(self, frame: str) -> None:
        event = json.loads(frame)
        self.sent.append(event)
        for reply in self.reply(event):
            self.incoming.put_nowait(reply)

    async def recv(self) -> str:
        return json.dumps(await self.incoming.get())

    async def close(self) -> None:
        self.incoming.put_nowait(None)

    async def __aiter__(self) -> AsyncIterator[str]:
        while (event := await self.incoming.get()) is not None:
            yield json.dumps(event)


def transport(ws: WebSocket) -> AbstractContextManager[Any]:
    @asynccontextmanager
    async def connect(
        url: str, *, additional_headers: dict[str, str]
    ) -> AsyncIterator[WebSocket]:
        ws.url = url  # type: ignore[attr-defined]
        try:
            yield ws
        finally:
            ws.closed = True

    return patch("celeste.providers.openai.live.client.ws_connect", connect)


def gpt_live(finalizes: bool) -> Callable[[dict[str, Any]], list[dict[str, Any]]]:
    def reply(event: dict[str, Any]) -> list[dict[str, Any]]:
        kind = event.get("type")
        if kind == "session.start":
            return [
                {
                    "type": "session.started",
                    "session": {
                        "audio": {"format": {"type": "audio/pcmu", "rate": 8000}}
                    },
                }
            ]
        if kind == "session.input_audio.append":
            return [
                {"type": "session.input_transcript.delta", "delta": "hi"},
                {
                    "type": "session.output_audio.delta",
                    "delta": base64.b64encode(b"xyz").decode(),
                },
                {"type": "session.output_transcript.delta", "delta": "yo"},
                {"type": "error", "error": {"message": "invalid command"}},
                {"type": "session.usage.updated", "usage": {"seconds": 3}},
            ]
        if kind == "session.close" and finalizes:
            return [
                {
                    "type": "session.closed",
                    "reason": "close_requested",
                    "usage": {"seconds": 4.5},
                }
            ]
        return []

    return reply


def test_catalog_streams_through_the_live_client() -> None:
    c = client()
    assert c.model.streaming is True
    assert c.model.operations == {Modality.LIVE: {Operation.CONNECT}}


@pytest.mark.parametrize(
    "shorthand",
    [
        "audio/pcm",
        "audio/pcm;rate=16000",
        "audio/pcm; rate=16000",
        AudioMimeType.PCMU,
        AudioMimeType.PCMA,
    ],
)
def test_audio_format_normalized_before_constraint(shorthand: str) -> None:
    body = client()._build_request(LiveInput(), audio_format=shorthand)
    assert body["session"]["audio"]["format"] in OPENAI_AUDIO_FORMATS
    assert (
        client()._build_request(
            LiveInput(), audio_format=body["session"]["audio"]["format"]
        )
        == body
    )
    with pytest.raises(ConstraintViolationError):
        client()._build_request(LiveInput(), audio_format="audio/wav")


def test_startup_roles_delegation_and_voice_catalog() -> None:
    inputs = LiveInput(
        messages=[
            Message(role=role, content=role.value)
            for role in (Role.SYSTEM, Role.DEVELOPER, Role.USER, Role.ASSISTANT)
        ]
    )
    body = client()._build_request(
        inputs,
        voice="marin",
        tools=[
            WebSearch(),
            {"name": "weather", "parameters": {"type": "object"}},
        ],
        extra_body={"delegation": {"responses": {"model": "gpt-5.4-mini"}}},
    )
    assert body["type"] == "session.start"
    session = body["session"]
    assert session["model"] == "gpt-live-1"
    assert session["instructions"] == "system"
    assert [item["role"] for item in session["input"]] == [
        "developer",
        "user",
        "assistant",
    ]
    assert [item["content"][0]["type"] for item in session["input"]] == [
        "input_text",
        "input_text",
        "output_text",
    ]
    assert session["delegation"] == {
        "type": "responses",
        "responses": {
            "model": "gpt-5.4-mini",
            "tools": [
                {"type": "web_search"},
                {
                    "type": "function",
                    "name": "weather",
                    "parameters": {"type": "object"},
                },
            ],
        },
    }
    with pytest.raises(ValueError, match="text messages only"):
        client()._build_request(
            LiveInput(messages=[ToolResult(tool_call_id="x", content="done")])
        )


def test_web_search_uses_the_responses_mapping() -> None:
    body = client()._build_request(
        LiveInput(), tools=[WebSearch(allowed_domains=["example.com"])]
    )
    assert body["session"]["delegation"]["responses"]["tools"] == [
        {"type": "web_search", "filters": {"allowed_domains": ["example.com"]}}
    ]
    with pytest.warns(UnsupportedParameterWarning, match="blocked_domains"):
        client()._build_request(
            LiveInput(), tools=[WebSearch(blocked_domains=["example.com"])]
        )


def test_parse_hooks_map_transcripts_delegated_tools_and_close() -> None:
    stream = object.__new__(OpenAILiveStream)
    transcript = stream._parse_chunk_transcript(
        {"type": "session.input_transcript.delta", "delta": "hello"}
    )
    assert transcript is not None
    assert (transcript.role, transcript.content) == (Role.USER, "hello")
    calls = stream._parse_chunk_tool_calls(
        {
            "type": "response.event",
            "delegation_id": "d",
            "event": {
                "type": "response.output_item.done",
                "item": {
                    "type": "function_call",
                    "call_id": "c",
                    "name": "weather",
                    "arguments": "{}",
                },
            },
        }
    )
    assert [(c.id, c.name, c.delegation_id) for c in calls] == [  # type: ignore[attr-defined]
        ("c", "weather", "d")
    ]
    assert stream._parse_stream_error({"type": "error", "error": {}}) is None
    closed = {
        "type": "session.closed",
        "reason": "close_requested",
        "usage": {"seconds": 2},
    }
    finish = stream._parse_chunk_finish_reason(closed)
    assert finish is not None
    assert finish.reason == "close_requested"
    assert stream._parse_chunk_usage(closed) == {"billed_units": 2}
    assert (
        stream._parse_chunk_finish_reason({"type": "session.output_audio.delta"})
        is None
    )


@pytest.mark.parametrize("finalizes", [True, False])
async def test_livestream_sends_in_order_and_ends_with_output(finalizes: bool) -> None:
    ws = WebSocket(gpt_live(finalizes))
    with (
        transport(ws),
        patch("celeste.providers.openai.live.config.CLOSE_TIMEOUT", 0.01),
    ):
        async with celeste.live.connect(
            model="gpt-live-1",
            provider=Provider.OPENAI,
            api_key="key",
            base_url="https://proxy.example/v1",
            audio_format=AudioMimeType.PCMU,
        ) as livestream:
            await livestream.send(
                AudioArtifact(data=b"pcm", mime_type=AudioMimeType.PCMU)
            )
            await livestream.send(
                ToolResult(tool_call_id="c", name="weather", content="sunny")
            )
            chunks = []
            async for chunk in livestream:
                chunks.append(chunk)
                if chunk.metadata["event_data"].get("type") == "session.usage.updated":
                    await livestream.end()
    assert ws.url == "wss://proxy.example/v1/live/sessions"  # type: ignore[attr-defined]
    assert [event["type"] for event in ws.sent] == [
        "session.start",
        "session.input_audio.append",
        "response.item.create",
        "session.close",
    ]
    assert ws.closed
    assert chunks[0].metadata["event_data"]["type"] == "session.started"
    output = livestream.output
    assert output.content.data == b"xyz"
    assert output.content.mime_type == AudioMimeType.PCMU
    assert output.content.metadata == {"sample_rate": 8000}
    assert output.usage.billed_units == (4.5 if finalizes else 3)
    assert (output.finish_reason.reason if output.finish_reason else None) == (
        "close_requested" if finalizes else None
    )
    assert [(m.role, m.content) for m in output.messages] == [
        (Role.USER, "sunny"),
        (Role.USER, "hi"),
        (Role.ASSISTANT, "yo"),
    ]
    assert all(
        "delta" not in event
        for event in output.metadata["raw_events"]
        if event.get("type") == "session.output_audio.delta"
    )


async def test_error_ack_raises_and_closes_socket() -> None:
    ws = WebSocket(
        lambda event: [{"type": "error", "error": {"message": "bad", "code": "x"}}]
    )
    with transport(ws), pytest.raises(StreamEventError, match="bad"):
        async with celeste.live.connect(
            model="gpt-live-1", api_key="key"
        ) as livestream:
            async for _ in livestream:
                pass
    assert ws.closed


async def test_text_messages_are_not_sendable() -> None:
    livestream = celeste.live.connect(model="gpt-live-1", api_key="key")
    with pytest.raises(NotImplementedError, match="messages"):
        await livestream.send("hello")
    await livestream.aclose()
