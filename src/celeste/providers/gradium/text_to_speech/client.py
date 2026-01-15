"""Gradium TextToSpeech API client mixin."""

import base64
import json
from collections.abc import AsyncIterator
from typing import Any

from websockets.asyncio.client import connect as ws_connect

from celeste.client import APIMixin
from celeste.io import FinishReason
from celeste.mime_types import AudioMimeType

from . import config


class GradiumTextToSpeechClient(APIMixin):
    """Mixin for Gradium Text-to-Speech API.

    Provides shared implementation for speech generation via WebSocket:
    - _make_stream_request() - WebSocket streaming (yields events)
    - _parse_usage() - Returns empty dict (TTS doesn't return usage)
    - _map_output_format_to_mime_type() - Map format string to AudioMimeType

    The Gradium Text-to-Speech API uses WebSocket instead of HTTP REST:
    1. Connect to wss://{region}.api.gradium.ai/api/speech/tts
    2. Send setup message with model, voice, format
    3. Receive ready confirmation
    4. Send text to synthesize
    5. Receive audio chunks (base64 encoded)
    6. Receive end message
    """

    async def _make_stream_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        **parameters: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """Execute WebSocket TTS flow as async generator.

        Yields events in streaming format:
        - {"data": bytes} for audio chunks
        - {"finish_reason": "stop"} at end

        Args:
            request_body: Request with text, voice_id, output_format, json_config.
            endpoint: WebSocket endpoint path (defaults to config).
            **parameters: Additional parameters (unused).

        Yields:
            Event dicts with audio data or finish_reason.

        Raises:
            ValueError: If connection fails or error received.
        """
        voice_id = request_body.get("voice_id", config.DEFAULT_VOICE_ID)
        output_format = request_body.get("output_format", "wav")
        text = request_body.get("text", "")
        json_config = request_body.get("json_config")

        if endpoint is None:
            endpoint = config.GradiumTextToSpeechEndpoint.CREATE_SPEECH
        url = f"{config.BASE_URL}{endpoint}"
        headers = self.auth.get_headers()

        async with ws_connect(url, additional_headers=headers) as ws:
            # 1. Send setup message
            setup_msg: dict[str, Any] = {
                "type": "setup",
                "model_name": self.model.id,
                "voice_id": voice_id,
                "output_format": output_format,
            }
            if json_config is not None:
                setup_msg["json_config"] = json_config

            await ws.send(json.dumps(setup_msg))

            # 2. Wait for ready
            ready_msg = await ws.recv()
            ready = json.loads(ready_msg)
            if ready.get("type") != "ready":
                msg = f"Expected ready message, got: {ready}"
                raise ValueError(msg)

            # 3. Send text
            await ws.send(json.dumps({"type": "text", "text": text}))

            # 4. Signal end of input
            await ws.send(json.dumps({"type": "end_of_stream"}))

            # 5. Yield audio chunks
            async for message in ws:
                if isinstance(message, bytes):
                    data = json.loads(message.decode("utf-8"))
                else:
                    data = json.loads(message)

                if data["type"] == "audio":
                    yield {"data": base64.b64decode(data["audio"])}
                elif data["type"] == "end_of_stream":
                    yield {"finish_reason": "stop"}
                    break
                elif data["type"] == "error":
                    error_msg = data.get("message", "Unknown error")
                    msg = f"Gradium TTS error: {error_msg}"
                    raise ValueError(msg)

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | float | None]:
        """Map Gradium usage fields to unified names.

        Gradium TTS doesn't provide usage metadata.
        """
        return {}

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """Extract usage data from Gradium API response.

        Gradium TTS doesn't provide usage metadata.
        Returns empty dict for capability clients to wrap in Usage type.
        """
        return GradiumTextToSpeechClient.map_usage_fields(response_data)

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Parse content from Gradium TTS response.

        Gradium uses WebSocket; base generate() should not call this.
        """
        msg = "Gradium TTS uses WebSocket; capability client must override generate()"
        raise NotImplementedError(msg)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """Gradium TTS doesn't provide finish reasons."""
        return FinishReason(reason=None)

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Collect audio from WebSocket stream.

        Calls _make_stream_request() and aggregates all audio chunks.
        """
        audio_chunks: list[bytes] = []
        output_format = request_body.get("output_format", "wav")

        async for event in self._make_stream_request(
            request_body, endpoint=endpoint, **parameters
        ):
            if "data" in event:
                audio_chunks.append(event["data"])

        return {
            "audio_bytes": b"".join(audio_chunks),
            "output_format": output_format,
        }

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary from response data."""
        return super()._build_metadata(response_data)

    def _map_output_format_to_mime_type(
        self,
        output_format: str | None,
    ) -> AudioMimeType:
        """Map Gradium output_format to AudioMimeType.

        Supported formats: wav, pcm, opus, ulaw_8000, alaw_8000, pcm_16000, pcm_24000.
        """
        format_map: dict[str, AudioMimeType] = {
            "wav": AudioMimeType.WAV,
            "pcm": AudioMimeType.WAV,  # PCM raw, closest match
            "opus": AudioMimeType.OGG,  # Opus in OGG container
            "ulaw_8000": AudioMimeType.WAV,
            "alaw_8000": AudioMimeType.WAV,
            "pcm_16000": AudioMimeType.WAV,
            "pcm_24000": AudioMimeType.WAV,
        }
        return format_map.get(output_format or "", AudioMimeType.WAV)


__all__ = ["GradiumTextToSpeechClient"]
