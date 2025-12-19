"""Gradium Text-to-Speech API client with shared implementation."""

import base64
import json
from typing import Any

from websockets.asyncio.client import connect as ws_connect

from celeste.client import APIMixin
from celeste.mime_types import AudioMimeType

from . import config


class GradiumTextToSpeechClient(APIMixin):
    """Mixin for Gradium Text-to-Speech API.

    Provides shared implementation for speech generation via WebSocket:
    - _websocket_tts() - Execute WebSocket TTS flow
    - _parse_usage() - Returns empty dict (TTS doesn't return usage)
    - _map_output_format_to_mime_type() - Map format string to AudioMimeType

    The Gradium Text-to-Speech API uses WebSocket instead of HTTP REST:
    1. Connect to wss://{region}.api.gradium.ai/api/speech/tts
    2. Send setup message with model, voice, format
    3. Receive ready confirmation
    4. Send text to synthesize
    5. Receive audio chunks (base64 encoded)
    6. Receive end message

    Subclasses override generate() to use _websocket_tts() instead of HTTP.

    Usage:
        class GradiumSpeechGenerationClient(GradiumTextToSpeechClient, SpeechGenerationClient):
            async def generate(self, *args, **parameters):
                # Build request...
                audio_data, format = await self._websocket_tts(request_body)
                # Return SpeechGenerationOutput...
    """

    async def _websocket_tts(
        self,
        request_body: dict[str, Any],
    ) -> tuple[bytes, str]:
        """Execute WebSocket TTS flow.

        Args:
            request_body: Request with text, voice_id, output_format, json_config.

        Returns:
            Tuple of (audio_bytes, output_format).

        Raises:
            ValueError: If connection fails or error received.
        """
        voice_id = request_body.get("voice_id", config.DEFAULT_VOICE_ID)
        output_format = request_body.get("output_format", "wav")
        text = request_body.get("text", "")
        json_config = request_body.get("json_config")

        url = f"{config.BASE_URL}{config.GradiumTextToSpeechEndpoint.CREATE_SPEECH}"
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

            # 5. Collect audio chunks
            audio_chunks: list[bytes] = []
            async for message in ws:
                if isinstance(message, bytes):
                    data = json.loads(message.decode("utf-8"))
                else:
                    data = json.loads(message)

                if data["type"] == "audio":
                    audio_chunks.append(base64.b64decode(data["audio"]))
                elif data["type"] == "end_of_stream":
                    break
                elif data["type"] == "error":
                    error_msg = data.get("message", "Unknown error")
                    msg = f"Gradium TTS error: {error_msg}"
                    raise ValueError(msg)

        return b"".join(audio_chunks), output_format

    def _parse_usage(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Extract usage data from Gradium API response.

        Gradium TTS doesn't provide usage metadata.
        Returns empty dict for capability clients to wrap in Usage type.
        """
        return {}

    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Any,
    ) -> Any:
        """Make HTTP request - not used for Gradium (uses WebSocket).

        Gradium TTS uses WebSocket via _websocket_tts().
        This method satisfies the abstract interface but should not be called.
        """
        msg = "Gradium TTS uses WebSocket, use _websocket_tts() instead"
        raise NotImplementedError(msg)

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
