"""Gradium client implementation for speech generation."""

import base64
import json
import logging
from typing import Any, Unpack

import httpx
import websockets

from celeste.artifacts import AudioArtifact
from celeste.mime_types import ApplicationMimeType
from celeste.parameters import ParameterMapper
from celeste_speech_generation.client import SpeechGenerationClient
from celeste_speech_generation.io import (
    SpeechGenerationInput,
    SpeechGenerationOutput,
    SpeechGenerationUsage,
)
from celeste_speech_generation.parameters import SpeechGenerationParameters

from . import config
from .parameters import GRADIUM_PARAMETER_MAPPERS
from .types import CreditsSummary, TTSResult, VoiceCreateResponse, VoiceInfo

logger = logging.getLogger(__name__)


class GradiumSpeechGenerationClient(SpeechGenerationClient):
    """Gradium client for speech generation (TTS).

    Supports:
    - Text-to-speech with streaming via WebSocket
    - 14 flagship voices + custom voice cloning
    - Multi-language support (en, fr, de, es, pt)
    - Speed control and audio formatting
    - Voice management (create/list/update/delete)
    - Credits monitoring
    """

    region: str = config.DEFAULT_REGION
    _base_url: str
    _ws_url: str

    def model_post_init(self, __context: object) -> None:
        """Initialize URLs based on region after model initialization."""
        super().model_post_init(__context)
        self._base_url = config.EU_BASE_URL if self.region == config.REGION_EU else config.US_BASE_URL
        self._ws_url = config.EU_TTS_WS_URL if self.region == config.REGION_EU else config.US_TTS_WS_URL

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return GRADIUM_PARAMETER_MAPPERS

    def _init_request(self, inputs: SpeechGenerationInput) -> dict[str, Any]:
        """Initialize request for Gradium TTS API format.

        Note: This is not directly used as Gradium uses WebSocket protocol.
        The actual request is built in the WebSocket message handler.
        """
        return {"text": inputs.text}

    def _parse_usage(self, response_data: dict[str, Any]) -> SpeechGenerationUsage:
        """Parse usage from Gradium response.

        Gradium doesn't provide usage metrics in WebSocket responses.
        Credits are calculated as 1 credit per character.
        """
        return SpeechGenerationUsage()

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[SpeechGenerationParameters],
    ) -> AudioArtifact:
        """Parse audio content from Gradium response.

        Args:
            response_data: Response containing audio data
            parameters: Generation parameters

        Returns:
            AudioArtifact with binary audio data
        """
        if "raw_data" in response_data:
            # Direct binary data
            return AudioArtifact(data=response_data["raw_data"])
        msg = "No audio data in response"
        raise ValueError(msg)

    async def _websocket_generate(
        self,
        text: str,
        voice_id: str,
        model_name: str = config.DEFAULT_MODEL,
        output_format: str = config.DEFAULT_FORMAT,
        json_config: dict[str, Any] | None = None,
    ) -> TTSResult:
        """Generate speech using WebSocket connection.

        Args:
            text: Text to convert to speech
            voice_id: Voice ID to use
            model_name: Model name (default: 'default')
            output_format: Audio format (wav, pcm, opus, etc.)
            json_config: Additional JSON configuration (e.g., padding_bonus)

        Returns:
            TTSResult with audio data and metadata
        """
        headers = {config.AUTH_HEADER_NAME: self.api_key.get_secret_value()}

        audio_chunks: list[bytes] = []
        request_id: str | None = None

        logger.info(f"Connecting to WebSocket: {self._ws_url}")
        try:
            async with websockets.connect(self._ws_url, additional_headers=headers) as websocket:
                logger.info("WebSocket connected successfully")

                # Send setup message (must be first)
                setup_msg = {
                    "type": config.WS_MSG_SETUP,
                    "model_name": model_name,
                    "voice_id": voice_id,
                    "output_format": output_format,
                }
                if json_config:
                    setup_msg["json_config"] = json_config

                logger.info(f"Sending setup message: {setup_msg}")
                await websocket.send(json.dumps(setup_msg))
                logger.info("Setup message sent, waiting for ready...")

                # Wait for ready message
                ready_msg = await websocket.recv()
                logger.info(f"Received message: {ready_msg[:200]}")
                ready_data = json.loads(ready_msg)

                if ready_data.get("type") != config.WS_MSG_READY:
                    msg = f"Expected ready message, got: {ready_data}"
                    raise ValueError(msg)

                request_id = ready_data.get("request_id")
                logger.info(f"Received ready message with request_id: {request_id}")

                # Send text message
                text_msg = {
                    "type": config.WS_MSG_TEXT,
                    "text": text,
                }
                logger.info(f"Sending text message: {text[:50]}...")
                await websocket.send(json.dumps(text_msg))
                logger.info("Text message sent")

                # Send end_of_stream to signal we're done sending text
                logger.info("Sending end_of_stream to signal completion")
                await websocket.send(json.dumps({"type": config.WS_MSG_END_OF_STREAM}))
                logger.info("End of stream sent, now receiving audio chunks...")

                # Receive audio chunks until server sends end_of_stream
                chunk_count = 0
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)

                    msg_type = data.get("type")
                    logger.info(f"Received message type: {msg_type}")

                    if msg_type == config.WS_MSG_AUDIO:
                        # Decode base64 audio data
                        audio_b64 = data.get("audio", "")
                        audio_data = base64.b64decode(audio_b64)
                        audio_chunks.append(audio_data)
                        chunk_count += 1
                        logger.info(f"Received audio chunk #{chunk_count}: {len(audio_data)} bytes")

                    elif msg_type == config.WS_MSG_END_OF_STREAM:
                        logger.info("Received end_of_stream from server - complete!")
                        break

                    elif msg_type == config.WS_MSG_ERROR:
                        error_msg = data.get("message", "Unknown error")
                        error_code = data.get("code")
                        logger.error(f"WebSocket error (code {error_code}): {error_msg}")
                        raise RuntimeError(f"WebSocket error (code {error_code}): {error_msg}")

                logger.info(f"WebSocket complete. Total chunks: {chunk_count}")

        except websockets.exceptions.WebSocketException as e:
            msg = f"WebSocket connection error: {e}"
            raise RuntimeError(msg) from e

        # Combine all audio chunks
        raw_data = b"".join(audio_chunks)

        # Determine sample rate based on output format
        sample_rate = config.PCM_SAMPLE_RATE  # Default 48kHz
        if "16000" in output_format:
            sample_rate = 16000
        elif "24000" in output_format:
            sample_rate = 24000
        elif "8000" in output_format:
            sample_rate = 8000

        return TTSResult(
            raw_data=raw_data,
            sample_rate=sample_rate,
            request_id=request_id,
        )

    async def generate(
        self,
        *args: str,
        **parameters: Unpack[SpeechGenerationParameters],
    ) -> SpeechGenerationOutput:
        """Generate speech from text.

        Args:
            text: Text to convert to speech (required)
            voice: Voice ID to use (required - e.g., 'YTpq7expH9539ERJ' for Emma)
            speed: Speed modifier -4.0 (faster) to 4.0 (slower), default 0.0
            response_format: Audio format (wav, pcm, opus, etc.), default 'wav'

        Returns:
            SpeechGenerationOutput with audio data
        """
        inputs = self._create_inputs(*args, **parameters)
        inputs, parameters = self._validate_artifacts(inputs, **parameters)
        request_body = self._build_request(inputs, **parameters)

        # Extract parameters
        voice_id = request_body.get("voice_id")
        if not voice_id:
            # Default to Emma if no voice specified
            voice_id = "YTpq7expH9539ERJ"

        model_name = self.model.id if self.model else config.DEFAULT_MODEL
        output_format = request_body.get("output_format", config.DEFAULT_FORMAT)
        json_config = request_body.get("json_config")

        logger.info(f"Generating speech with Gradium (voice: {voice_id}, format: {output_format})")

        # Generate via WebSocket
        result = await self._websocket_generate(
            text=inputs.text,
            voice_id=voice_id,
            model_name=model_name,
            output_format=output_format,
            json_config=json_config,
        )

        # Build metadata
        metadata = {
            "request_id": result.request_id,
            "sample_rate": result.sample_rate,
            "region": self.region,
        }

        return self._output_class()(
            content=AudioArtifact(data=result.raw_data),
            usage=self._parse_usage({}),
            metadata=metadata,
        )

    # Voice Management Methods

    async def list_voices(
        self,
        skip: int = 0,
        limit: int = 100,
        include_catalog: bool = False,
    ) -> list[VoiceInfo]:
        """List available voices.

        Args:
            skip: Number of voices to skip (pagination)
            limit: Maximum number of voices to return
            include_catalog: Include catalog voices in addition to custom voices

        Returns:
            List of voice information objects
        """
        headers = {
            config.AUTH_HEADER_NAME: self.api_key.get_secret_value(),
            "Content-Type": str(ApplicationMimeType.JSON),
        }

        params = {
            "skip": skip,
            "limit": limit,
            "include_catalog": include_catalog,
        }

        response = await self.http_client.get(
            f"{self._base_url}{config.VOICES_ENDPOINT}",
            headers=headers,
            params=params,
        )

        if response.status_code >= 400:
            response.raise_for_status()

        data = response.json()
        return [VoiceInfo(**voice) for voice in data]

    async def get_voice(self, voice_uid: str) -> VoiceInfo:
        """Get information about a specific voice.

        Args:
            voice_uid: Unique identifier of the voice

        Returns:
            Voice information object
        """
        headers = {
            config.AUTH_HEADER_NAME: self.api_key.get_secret_value(),
            "Content-Type": str(ApplicationMimeType.JSON),
        }

        url = f"{self._base_url}{config.VOICE_DETAIL_ENDPOINT.format(voice_uid=voice_uid)}"
        response = await self.http_client.get(url, headers=headers)

        if response.status_code >= 400:
            response.raise_for_status()

        return VoiceInfo(**response.json())

    async def create_voice(
        self,
        audio_file: str | bytes,
        name: str,
        input_format: str = "wav",
        description: str | None = None,
        language: str | None = None,
        start_s: float = 0.0,
        timeout_s: float = 10.0,
    ) -> VoiceCreateResponse:
        """Create a custom voice from audio sample.

        Args:
            audio_file: Path to audio file or raw audio bytes
            name: Name for the voice
            input_format: Audio format (wav, mp3, etc.)
            description: Optional description
            language: Optional language code
            start_s: Start time in audio file (seconds)
            timeout_s: Timeout for voice creation (seconds)

        Returns:
            Voice creation response with UID
        """
        headers = {
            config.AUTH_HEADER_NAME: self.api_key.get_secret_value(),
        }

        # Prepare audio data
        if isinstance(audio_file, str):
            with open(audio_file, "rb") as f:
                audio_data = f.read()
        else:
            audio_data = audio_file

        # Prepare form data
        files = {"audio_file": ("audio.wav", audio_data, "audio/wav")}
        data = {
            "name": name,
            "input_format": input_format,
            "start_s": start_s,
            "timeout_s": timeout_s,
        }

        if description:
            data["description"] = description
        if language:
            data["language"] = language

        # Use httpx directly for multipart form data
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._base_url}{config.VOICES_ENDPOINT}",
                headers=headers,
                files=files,
                data=data,
            )

        if response.status_code >= 400:
            response.raise_for_status()

        return VoiceCreateResponse(**response.json())

    async def update_voice(
        self,
        voice_uid: str,
        name: str | None = None,
        description: str | None = None,
        language: str | None = None,
        start_s: float | None = None,
    ) -> VoiceInfo:
        """Update a custom voice.

        Args:
            voice_uid: Unique identifier of the voice
            name: New name (optional)
            description: New description (optional)
            language: New language code (optional)
            start_s: New start time (optional)

        Returns:
            Updated voice information
        """
        headers = {
            config.AUTH_HEADER_NAME: self.api_key.get_secret_value(),
            "Content-Type": str(ApplicationMimeType.JSON),
        }

        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if language is not None:
            data["language"] = language
        if start_s is not None:
            data["start_s"] = start_s

        url = f"{self._base_url}{config.VOICE_DETAIL_ENDPOINT.format(voice_uid=voice_uid)}"
        response = await self.http_client.put(
            url,
            headers=headers,
            json_body=data,
        )

        if response.status_code >= 400:
            response.raise_for_status()

        return VoiceInfo(**response.json())

    async def delete_voice(self, voice_uid: str) -> None:
        """Delete a custom voice.

        Args:
            voice_uid: Unique identifier of the voice
        """
        headers = {
            config.AUTH_HEADER_NAME: self.api_key.get_secret_value(),
        }

        url = f"{self._base_url}{config.VOICE_DETAIL_ENDPOINT.format(voice_uid=voice_uid)}"
        response = await self.http_client.delete(url, headers=headers)

        if response.status_code >= 400:
            response.raise_for_status()

    # Credits Management

    async def get_credits(self) -> CreditsSummary:
        """Get current credit balance and usage information.

        Returns:
            Credits summary with balance and billing information
        """
        headers = {
            config.AUTH_HEADER_NAME: self.api_key.get_secret_value(),
            "Content-Type": str(ApplicationMimeType.JSON),
        }

        response = await self.http_client.get(
            f"{self._base_url}{config.CREDITS_ENDPOINT}",
            headers=headers,
        )

        if response.status_code >= 400:
            response.raise_for_status()

        return CreditsSummary(**response.json())

    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[SpeechGenerationParameters],
    ) -> httpx.Response:
        """Make HTTP request and return response object.

        Note: Overridden by generate() for Gradium WebSocket-based TTS.
        """
        msg = "Use generate() for Gradium TTS (WebSocket-based)"
        raise NotImplementedError(msg)


__all__ = ["GradiumSpeechGenerationClient"]
