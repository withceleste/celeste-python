"""Google Live API client mixin."""

import asyncio
import base64
import json
from collections.abc import AsyncGenerator
from typing import Any
from urllib.parse import urlsplit

from websockets.asyncio.client import ClientConnection
from websockets.asyncio.client import connect as ws_connect
from websockets.exceptions import ConnectionClosed

from celeste.client import APIMixin
from celeste.core import UsageField
from celeste.providers.google.auth import GoogleADC
from celeste.types import RawUsage

from . import config


def _split_event(event: dict[str, Any]) -> list[dict[str, Any]]:
    """Yield the input transcript before output in a shared frame, usage kept on the second."""
    content = event.get("serverContent", {})
    if "inputTranscription" in content and (
        "outputTranscription" in content or "modelTurn" in content
    ):
        return [
            {"serverContent": {"inputTranscription": content["inputTranscription"]}},
            {
                **event,
                "serverContent": {
                    k: v for k, v in content.items() if k != "inputTranscription"
                },
            },
        ]
    return [event]


def _decode_audio(event: dict[str, Any]) -> dict[str, Any]:
    """Decode base64 inline audio in place so chunk content and event data share the bytes."""
    for part in event.get("serverContent", {}).get("modelTurn", {}).get("parts", []):
        inline = part.get("inlineData", {})
        if isinstance(inline.get("data"), str):
            inline["data"] = base64.b64decode(inline["data"])
    return event


class GoogleLiveClient(APIMixin):
    """Mixin for Google Live API.

    Provides the WebSocket transport for live streaming:
    - _make_stream_request() - Returns the Live event generator
    - _parse_usage() - Extract usage dict from an event

    The Google Live API is bidirectional over one WebSocket:
    1. Send setup and await setupComplete
    2. Send the seeded history, if any
    3. Receive server events while a sender task writes queued client frames
    4. end() closes the socket; Google has no client close message
    """

    def _build_request(
        self,
        inputs: Any,
        extra_body: dict[str, Any] | None = None,
        streaming: bool = False,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Merge extra_body into setup, keeping history outside the setup frame."""
        body = super()._build_request(
            inputs, extra_body=None, streaming=streaming, **parameters
        )
        seed = body.pop("clientContent", None)
        if extra_body:
            self._deep_merge(body, extra_body)
        result = {"setup": body}
        if (
            seed
            and seed["turns"]
            and not (body.get("sessionResumption") or {}).get("handle")
        ):
            result["clientContent"] = seed
        return result

    def _get_vertex_endpoint(self, native_endpoint: str) -> str:
        """Map native endpoint to Vertex AI endpoint."""
        mapping: dict[str, str] = {
            config.GoogleLiveEndpoint.BIDI_GENERATE_CONTENT: config.VertexLiveEndpoint.BIDI_GENERATE_CONTENT,
        }
        vertex_endpoint = mapping.get(native_endpoint)
        if vertex_endpoint is None:
            raise ValueError(f"No Vertex AI endpoint mapping for: {native_endpoint}")
        return vertex_endpoint

    def _build_url(self, endpoint: str) -> str:
        """Build the WebSocket URL based on auth type; base_url replaces the host."""
        if isinstance(self.auth, GoogleADC):
            url = self.auth.build_url(
                self._get_vertex_endpoint(endpoint), model_id=self.model.id
            )
        else:
            url = f"{config.BASE_URL}{endpoint}"
        if self.base_url:
            url = f"{self.base_url.rstrip('/')}{urlsplit(url).path}"
        return url.replace("https://", "wss://", 1).replace("http://", "ws://", 1)

    def _model_resource_name(self) -> str:
        """Setup model name; call after _build_url has checked the Vertex project."""
        if isinstance(self.auth, GoogleADC):
            return (
                f"projects/{self.auth.resolved_project_id}/locations/"
                f"{self.auth.location}/publishers/google/models/{self.model.id}"
            )
        return f"models/{self.model.id}"

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
        url = self._build_url(
            endpoint or config.GoogleLiveEndpoint.BIDI_GENERATE_CONTENT
        )
        return self._stream_events(url, headers, request_body)

    async def _stream_events(
        self,
        url: str,
        headers: dict[str, str],
        request_body: dict[str, Any],
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Yield server events while a sender task writes the livestream's queued frames."""
        setup = {**request_body["setup"], "model": self._model_resource_name()}
        async with ws_connect(url, additional_headers=headers) as ws:
            await ws.send(json.dumps({"setup": setup}))
            ack = json.loads(await ws.recv())
            if "setupComplete" not in ack:
                msg = f"Unexpected Google Live setup acknowledgement: {ack}"
                raise ValueError(msg)
            if "clientContent" in request_body:
                await ws.send(
                    json.dumps({"clientContent": request_body["clientContent"]})
                )
            handoff: dict[str, Any] = {"outbound": None}
            yield handoff
            ended = asyncio.Event()
            sender = asyncio.create_task(
                self._send_frames(ws, handoff["outbound"], ended)
            )
            try:
                yield ack
                async for message in ws:
                    for event in _split_event(json.loads(message)):
                        yield _decode_audio(event)
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
        """Write queued frames in order; the end marker closes the socket."""
        while (frame := await outbound.get()) is not None:
            await ws.send(frame)
        ended.set()
        await ws.close()

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Google Live is stream-only; use connect()."""
        msg = "Google Live is stream-only; use celeste.live.connect()"
        raise NotImplementedError(msg)

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Google Live is stream-only; content arrives as chunks."""
        msg = "Google Live is stream-only; use celeste.live.connect()"
        raise NotImplementedError(msg)

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | float | None]:
        """Map Google Live usage fields to unified names."""
        return {
            UsageField.INPUT_TOKENS: usage_data.get("promptTokenCount"),
            UsageField.OUTPUT_TOKENS: usage_data.get("responseTokenCount"),
            UsageField.TOTAL_TOKENS: usage_data.get("totalTokenCount"),
            UsageField.REASONING_TOKENS: usage_data.get("thoughtsTokenCount"),
            UsageField.CACHED_TOKENS: usage_data.get("cachedContentTokenCount"),
        }

    def _parse_usage(self, response_data: dict[str, Any]) -> RawUsage:
        """Extract usage data from a Google Live event."""
        return self.map_usage_fields(response_data.get("usageMetadata", {}))
