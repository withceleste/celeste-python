"""OpenAI Live API client mixin."""

import asyncio
import base64
import json
from collections.abc import AsyncGenerator
from typing import Any

from websockets.asyncio.client import ClientConnection
from websockets.asyncio.client import connect as ws_connect
from websockets.exceptions import ConnectionClosed

from celeste.client import APIMixin
from celeste.core import UsageField
from celeste.exceptions import StreamEventError
from celeste.types import RawUsage

from . import config


class OpenAILiveClient(APIMixin):
    """Mixin for OpenAI Live API.

    Provides the WebSocket transport for live streaming:
    - _make_stream_request() - Returns the Live event generator
    - _parse_usage() - Extract usage dict from an event

    The OpenAI Live primary WebSocket is full duplex:
    1. Send session.start and await session.started
    2. Receive server events while a sender task writes queued client events
    3. end() sends session.close; the stream ends after session.closed
    """

    def _build_request(
        self,
        inputs: Any,
        extra_body: dict[str, Any] | None = None,
        streaming: bool = False,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Wrap the session configuration, including extra_body, in session.start."""
        session = super()._build_request(
            inputs, extra_body=extra_body, streaming=streaming, **parameters
        )
        session["model"] = self.model.id
        return {"type": "session.start", "session": session}

    async def _make_stream_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Any,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Return the WebSocket event generator."""
        headers = self._merge_headers(await self.auth.aget_headers(), extra_headers)
        base = (self.base_url or config.BASE_URL).rstrip("/").removesuffix("/v1")
        url = base.replace("https://", "wss://", 1).replace("http://", "ws://", 1) + (
            endpoint or config.OpenAILiveEndpoint.CREATE_SESSION
        )
        return self._stream_events(url, headers, request_body)

    async def _stream_events(
        self,
        url: str,
        headers: dict[str, str],
        request_body: dict[str, Any],
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Yield server events while a sender task writes the livestream's queued events."""
        async with ws_connect(url, additional_headers=headers) as ws:
            await ws.send(json.dumps(request_body))
            ack = json.loads(await ws.recv())
            if ack.get("type") == "error":
                error = ack.get("error", {})
                raise StreamEventError(
                    message=error.get("message", "Live startup failed"),
                    error_type=error.get("code"),
                    event_data=ack,
                    provider=self.provider,
                )
            if ack.get("type") != "session.started":
                msg = f"Unexpected OpenAI Live startup acknowledgement: {ack}"
                raise ValueError(msg)
            handoff: dict[str, Any] = {"outbound": None}
            yield handoff
            ended = asyncio.Event()
            sender = asyncio.create_task(
                self._send_frames(ws, handoff["outbound"], ended)
            )
            try:
                yield ack
                async for message in ws:
                    event = json.loads(message)
                    if event.get("type") == "session.output_audio.delta":
                        event["delta"] = base64.b64decode(event["delta"])
                    yield event
                    if event.get("type") == "session.closed":
                        return
            except ConnectionClosed:
                if not ended.is_set():
                    raise
            finally:
                sender.cancel()
                await asyncio.gather(sender, return_exceptions=True)

    @staticmethod
    async def _send_frames(
        ws: ClientConnection,
        outbound: asyncio.Queue[str | None],
        ended: asyncio.Event,
    ) -> None:
        """Write queued events in order; the end marker requests session.close."""
        while (frame := await outbound.get()) is not None:
            await ws.send(frame)
        ended.set()
        await ws.send(json.dumps({"type": "session.close"}))
        await asyncio.sleep(config.CLOSE_TIMEOUT)
        await ws.close()

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        """OpenAI Live is stream-only; use connect()."""
        msg = "OpenAI Live is stream-only; use celeste.live.connect()"
        raise NotImplementedError(msg)

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """OpenAI Live is stream-only; content arrives as chunks."""
        msg = "OpenAI Live is stream-only; use celeste.live.connect()"
        raise NotImplementedError(msg)

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | float | None]:
        """Map OpenAI Live usage fields to unified names; seconds are cumulative."""
        return {UsageField.BILLED_UNITS: usage_data.get("seconds")}

    def _parse_usage(self, response_data: dict[str, Any]) -> RawUsage:
        """Extract usage data from an OpenAI Live event."""
        return self.map_usage_fields(response_data.get("usage", {}))


__all__ = ["OpenAILiveClient"]
