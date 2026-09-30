"""Google Live request building, event parsing, and WebSocket transport."""

import asyncio
import base64
import json
from collections.abc import AsyncIterator, Callable
from contextlib import AbstractContextManager, asynccontextmanager
from typing import Any
from unittest.mock import patch

import pytest
from websockets.exceptions import ConnectionClosedError

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
from celeste.artifacts import AudioArtifact, ImageArtifact
from celeste.auth import NoAuth
from celeste.exceptions import StreamNotExhaustedError, UnsupportedParameterWarning
from celeste.mime_types import AudioMimeType, ImageMimeType
from celeste.modalities.live.client import LiveClient
from celeste.modalities.live.io import LiveChunk, LiveInput, LiveUsage
from celeste.modalities.live.providers.google.client import GoogleLiveStream
from celeste.providers.google.auth import GoogleADC
from celeste.tools import ToolCall, WebSearch
from celeste.types import ImagePart, TextPart


def client(model: str = "gemini-3.8-live") -> LiveClient:
    result = create_client(modality=Modality.LIVE, model=model, auth=NoAuth())
    assert isinstance(result, LiveClient)
    return result


class WebSocket:
    """Scripted server: each client frame may queue server events in reply."""

    def __init__(
        self,
        reply: Callable[[dict[str, Any]], list[dict[str, Any]]],
        *,
        close_error: bool = False,
    ) -> None:
        self.reply = reply
        self.close_error = close_error
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
        if self.close_error:
            raise ConnectionClosedError(None, None)


def transport(ws: WebSocket) -> AbstractContextManager[Any]:
    @asynccontextmanager
    async def connect(
        url: str, *, additional_headers: dict[str, str]
    ) -> AsyncIterator[WebSocket]:
        ws.url = url  # type: ignore[attr-defined]
        ws.headers = additional_headers  # type: ignore[attr-defined]
        try:
            yield ws
        finally:
            ws.closed = True

    return patch("celeste.providers.google.live.client.ws_connect", connect)


def gemini(event: dict[str, Any]) -> list[dict[str, Any]]:
    if "setup" in event:
        return [{"setupComplete": {}}]
    if event.get("clientContent", {}).get("turnComplete"):
        return [
            {
                "serverContent": {
                    "inputTranscription": {"text": "hi"},
                    "outputTranscription": {"text": "Hel"},
                    "modelTurn": {
                        "parts": [
                            {
                                "inlineData": {
                                    "mimeType": "audio/pcm;rate=24000",
                                    "data": base64.b64encode(b"abc").decode(),
                                }
                            }
                        ]
                    },
                }
            },
            {
                "serverContent": {"outputTranscription": {"text": "lo"}},
                "toolCall": {
                    "functionCalls": [{"id": "1", "name": "weather", "args": {}}]
                },
            },
            {
                "serverContent": {"turnComplete": True},
                "usageMetadata": {"promptTokenCount": 5, "totalTokenCount": 9},
            },
        ]
    return []


def test_unregistered_live_model_uses_the_live_client() -> None:
    with pytest.warns(UserWarning, match="not registered"):
        c = create_client(
            modality=Modality.LIVE,
            provider=Provider.GOOGLE,
            model="future-live",
            operation=Operation.CONNECT,
            auth=NoAuth(),
        )
    assert isinstance(c, LiveClient)
    assert c.model.operations == {Modality.LIVE: {Operation.CONNECT}}


@pytest.mark.parametrize(
    "model", ["gemini-3.8-live", "gemini-3.8-live-extended-thinking"]
)
def test_catalog_streams_through_the_live_client(model: str) -> None:
    c = client(model)
    assert c.model.streaming is True
    assert c.model.operations == {Modality.LIVE: {Operation.CONNECT}}


def test_setup_seed_tools_and_resumption() -> None:
    c = client("gemini-3.8-live-extended-thinking")
    inputs = LiveInput(
        messages=[
            Message(role=Role.SYSTEM, content="be brief"),
            Message(
                role=Role.ASSISTANT,
                content="",
                tool_calls=[ToolCall(id="1", name="weather", arguments={})],
            ),
            ToolResult(tool_call_id="1", name="weather", content={"ok": True}),
        ],
    )
    body = c._build_request(
        inputs,
        thinking_level="LOW",
        tools=[WebSearch(), {"name": "weather", "parameters": {"type": "object"}}],
        extra_body={"generationConfig": {"temperature": 0.3}},
    )
    setup = body["setup"]
    assert setup["generationConfig"] == {
        "responseModalities": ["AUDIO"],
        "thinkingConfig": {"thinkingLevel": "LOW"},
        "temperature": 0.3,
    }
    assert setup["systemInstruction"] == {"parts": [{"text": "be brief"}]}
    assert body["clientContent"]["turnComplete"] is False
    assert body["clientContent"]["turns"][0]["parts"][-1]["functionCall"]["id"] == "1"
    resumed = c._build_request(
        inputs, extra_body={"sessionResumption": {"handle": "saved"}}
    )
    assert "clientContent" not in resumed
    audio = client()._build_request(
        LiveInput(), extra_body={"outputAudioTranscription": None}
    )
    assert audio["setup"]["outputAudioTranscription"] is None
    assert audio["setup"]["inputAudioTranscription"] == {}


def test_unsupported_language_is_not_mapped() -> None:
    with pytest.warns(UnsupportedParameterWarning, match="language"):
        body = client()._build_request(LiveInput(), language="fr")
    assert "speechConfig" not in body["setup"]["generationConfig"]


@pytest.mark.parametrize(
    ("events", "reasons"),
    [
        ([{"turnComplete": True}], ["turnComplete"]),
        (
            [{"interrupted": True}, {"turnComplete": True}, {"turnComplete": True}],
            [None, "interrupted", "turnComplete"],
        ),
        (
            [{"interrupted": True, "turnComplete": True}, {"turnComplete": True}],
            ["interrupted", "turnComplete"],
        ),
        (
            [
                {"turnComplete": True, "interactionStatus": "IN_PROGRESS"},
                {"turnComplete": True, "interactionStatus": "IDLE"},
            ],
            [None, "turnComplete"],
        ),
    ],
    ids=["normal", "interrupted", "same-event", "in-progress"],
)
def test_one_finish_reason_per_model_turn(
    events: list[dict[str, Any]], reasons: list[str | None]
) -> None:
    stream = object.__new__(GoogleLiveStream)
    parsed = [
        stream._parse_chunk_finish_reason({"serverContent": content})
        for content in events
    ]
    assert [r.reason if r else None for r in parsed] == reasons


@pytest.mark.parametrize(
    ("events", "input_tokens"),
    [
        (
            [
                {"serverContent": {"turnComplete": True}, "usage": 549},
                {"serverContent": {"turnComplete": True}, "usage": 630},
            ],
            1179,
        ),
        (
            [
                {"serverContent": {"interrupted": True}, "usage": 5},
                {"serverContent": {"turnComplete": True}, "usage": 6},
            ],
            6,
        ),
        (
            [
                {"serverContent": {"turnComplete": True}, "usage": 4},
                {"serverContent": {}, "usage": 7},
            ],
            11,
        ),
    ],
    ids=["turns-summed", "interim-replaced", "trailing-turn"],
)
def test_usage_sums_the_last_snapshot_of_each_turn(
    events: list[dict[str, Any]], input_tokens: int
) -> None:
    chunks = [
        LiveChunk(
            content=b"",
            usage=LiveUsage(input_tokens=event.pop("usage")),
            metadata={"event_data": event},
        )
        for event in events
    ]
    usage = object.__new__(GoogleLiveStream)._aggregate_usage(chunks)
    assert usage.input_tokens == input_tokens


def test_serialization_uses_typed_parts_and_wire_escape_hatches() -> None:
    stream = object.__new__(GoogleLiveStream)
    image = ImageArtifact(data=b"abc", mime_type=ImageMimeType.PNG)
    assert stream._serialize_message(
        Message(
            role=Role.USER,
            content=[ImagePart(image=image), TextPart(text="describe")],
        )
    ) == [
        {
            "clientContent": {
                "turns": [
                    {
                        "role": "user",
                        "parts": [
                            {"inline_data": {"mime_type": "image/png", "data": "YWJj"}},
                            {"text": "describe"},
                        ],
                    }
                ],
                "turnComplete": True,
            }
        }
    ]
    assert stream._serialize_audio(
        AudioArtifact(
            data=b"abc", mime_type=AudioMimeType.PCM, metadata={"sample_rate": 24000}
        )
    )[0]["realtimeInput"]["audio"] == {
        "data": "YWJj",
        "mimeType": "audio/pcm;rate=24000",
    }
    assert (
        stream._serialize_image(image)[0]["realtimeInput"]["video"]["mimeType"]
        == "image/png"
    )
    with pytest.raises(ValueError, match="setup"):
        stream._serialize_message(Message(role=Role.SYSTEM, content="no"))


@pytest.mark.parametrize("close_error", [False, True])
async def test_livestream_sends_in_order_and_ends_with_output(
    close_error: bool,
) -> None:
    ws = WebSocket(gemini, close_error=close_error)
    with transport(ws):
        async with celeste.live.connect(
            model="gemini-3.8-live",
            api_key="key",
            messages=[Message(role=Role.USER, content="old")],
            reference_images=[ImageArtifact(data=b"abc", mime_type=ImageMimeType.PNG)],
        ) as livestream:
            await livestream.send("new")
            chunks = []
            async for chunk in livestream:
                chunks.append(chunk)
                if chunk.finish_reason:
                    await livestream.end()
    assert [list(frame) for frame in ws.sent] == [
        ["setup"],
        ["clientContent"],
        ["clientContent"],
    ]
    assert ws.sent[0]["setup"]["model"] == "models/gemini-3.8-live"
    assert ws.sent[1]["clientContent"]["turns"][0] == {
        "role": "user",
        "parts": [{"text": "old"}],
    }
    assert ws.sent[2]["clientContent"]["turnComplete"] is True
    assert ws.closed
    assert "v1beta.GenerativeService" in ws.url  # type: ignore[attr-defined]
    assert ws.headers["x-goog-api-key"] == "key"  # type: ignore[attr-defined]
    assert [chunk.content for chunk in chunks] == [b"", b"", b"abc", b"", b""]
    assert chunks[3].tool_calls[0].name == "weather"
    output = livestream.output
    assert output.content.data == b"abc"
    assert output.content.metadata == {"sample_rate": 24000}
    assert output.usage.input_tokens == 5
    assert output.finish_reason is not None
    assert output.finish_reason.reason == "turnComplete"
    assert [(m.role, m.content) for m in output.messages] == [
        (Role.USER, "new"),
        (Role.USER, "hi"),
        (Role.ASSISTANT, "Hello"),
        (Role.ASSISTANT, ""),
    ]
    assert output.tool_calls[0].id == "1"
    assert all(
        "data" not in part.get("inlineData", {})
        for event in output.metadata["raw_events"]
        for part in event.get("serverContent", {}).get("modelTurn", {}).get("parts", [])
    )


async def test_unexpected_ack_raises_and_closes_socket() -> None:
    ws = WebSocket(lambda event: [{"unexpected": True}])
    with transport(ws), pytest.raises(ValueError, match="acknowledgement"):
        async with celeste.live.connect(
            model="gemini-3.8-live", api_key="key"
        ) as livestream:
            async for _ in livestream:
                pass
    assert ws.closed
    with pytest.raises(RuntimeError, match="ended"):
        await livestream.send("late")


async def test_aclose_aborts_without_output() -> None:
    ws = WebSocket(gemini)
    with transport(ws):
        async with celeste.live.connect(
            model="gemini-3.8-live", api_key="key"
        ) as livestream:
            await livestream.send("hello")
            await anext(livestream)
    assert ws.closed
    with pytest.raises(StreamNotExhaustedError):
        _ = livestream.output


async def test_vertex_auth_resolved_before_model_resource() -> None:
    ws = WebSocket(lambda event: [{"setupComplete": {}}] if "setup" in event else [])
    auth = GoogleADC(location="us-central1")

    async def headers() -> dict[str, str]:
        auth.project_id = "resolved-project"
        return {"Authorization": "Bearer test"}

    with patch.object(GoogleADC, "aget_headers", side_effect=headers), transport(ws):
        async with celeste.live.connect(
            model="gemini-3.8-live", auth=auth
        ) as livestream:
            await anext(livestream)
    assert (
        ws.sent[0]["setup"]["model"]
        == "projects/resolved-project/locations/us-central1/publishers/google/models/gemini-3.8-live"
    )
    assert (
        ws.url  # type: ignore[attr-defined]
        == "wss://us-central1-aiplatform.googleapis.com/ws/google.cloud.aiplatform.v1.LlmBidiService/BidiGenerateContent"
    )
