"""WebSocket ownership for Gradium's streaming and unary consumers."""

import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch

import pytest

from celeste import Modality, Provider, create_client
from celeste.auth import NoAuth
from celeste.providers.gradium.text_to_speech import config


@pytest.mark.parametrize("mode", ["unary", "stream", "early", "error"])
async def test_gradium_consumers_close_websocket(mode: str) -> None:
    class WebSocket:
        closed = False
        send = AsyncMock()
        recv = AsyncMock(return_value='{"type":"ready"}')

        async def __aiter__(self) -> AsyncIterator[str]:
            yield '{"type":"audio","audio":"aGVsbG8="}'
            if mode == "error":
                yield '{"type":"error","message":"failed"}'
            else:
                yield '{"type":"end_of_stream"}'

    ws = WebSocket()

    @asynccontextmanager
    async def connect(
        url: str, *, additional_headers: dict[str, str]
    ) -> AsyncIterator[WebSocket]:
        assert (
            url
            == f"{config.BASE_URL}{config.GradiumTextToSpeechEndpoint.CREATE_SPEECH}"
        )
        assert additional_headers == {"X-Test": "yes"}
        try:
            yield ws
        finally:
            ws.closed = True

    client = create_client(
        modality=Modality.AUDIO,
        provider=Provider.GRADIUM,
        model="default",
        auth=NoAuth(),
    )
    with patch("celeste.providers.gradium.text_to_speech.client.ws_connect", connect):
        if mode in {"unary", "error"}:
            if mode == "error":
                with pytest.raises(ValueError, match="Gradium TTS error: failed"):
                    await client.speak("hello", extra_headers={"X-Test": "yes"})
            else:
                output = await client.speak("hello", extra_headers={"X-Test": "yes"})
                assert output.content.data == b"hello"
        else:
            stream = client.stream.speak("hello", extra_headers={"X-Test": "yes"})
            assert (await anext(stream)).content == b"hello"
            if mode == "stream":
                _ = [chunk async for chunk in stream]
                assert stream.output.content.data == b"hello"
            await stream.aclose()
        assert ws.closed
    assert [json.loads(call.args[0]) for call in ws.send.await_args_list] == [
        {
            "type": "setup",
            "model_name": "default",
            "voice_id": config.DEFAULT_VOICE_ID,
            "output_format": "wav",
        },
        {"type": "text", "text": "hello"},
        {"type": "end_of_stream"},
    ]
