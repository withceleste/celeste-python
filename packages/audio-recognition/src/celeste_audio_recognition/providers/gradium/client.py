"""Gradium client implementation for audio recognition (STT)."""

import asyncio
import base64
import json
import logging
from collections.abc import AsyncGenerator
from typing import Any, Unpack

import httpx
import websockets

from celeste.parameters import ParameterMapper
from celeste_audio_recognition.client import AudioRecognitionClient
from celeste_audio_recognition.io import (
    AudioRecognitionChunk,
    AudioRecognitionInput,
    AudioRecognitionOutput,
    AudioRecognitionUsage,
)
from celeste_audio_recognition.parameters import AudioRecognitionParameters

from . import config
from .parameters import GRADIUM_PARAMETER_MAPPERS
from .types import STTResult, TranscriptionSegment, VADPrediction, VADStep

logger = logging.getLogger(__name__)


class GradiumAudioRecognitionClient(AudioRecognitionClient):
    """Gradium client for audio recognition (STT).

    Supports:
    - Speech-to-text with streaming via WebSocket
    - Multi-language support (auto-detected)
    - Voice Activity Detection (VAD)
    - Real-time transcription with timestamps
    - Multiple audio formats (pcm, wav, opus)
    """

    region: str = config.DEFAULT_REGION
    _ws_url: str

    def model_post_init(self, __context: object) -> None:
        """Initialize WebSocket URL based on region after model initialization."""
        super().model_post_init(__context)
        self._ws_url = config.EU_STT_WS_URL if self.region == config.REGION_EU else config.US_STT_WS_URL

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return GRADIUM_PARAMETER_MAPPERS

    def _init_request(self, inputs: AudioRecognitionInput) -> dict[str, Any]:
        """Initialize request for Gradium STT API format.

        Note: This is not directly used as Gradium uses WebSocket protocol.
        The actual request is built in the WebSocket message handler.
        """
        return {"input_format": inputs.format}

    def _parse_usage(self, response_data: dict[str, Any]) -> AudioRecognitionUsage:
        """Parse usage from Gradium response.

        Args:
            response_data: Response containing usage data

        Returns:
            AudioRecognitionUsage with metrics
        """
        characters = response_data.get("characters")
        duration_s = response_data.get("duration_s")
        return AudioRecognitionUsage(characters=characters, duration_s=duration_s)

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[AudioRecognitionParameters],
    ) -> str:
        """Parse transcribed text from Gradium response.

        Args:
            response_data: Response containing transcription
            parameters: Recognition parameters

        Returns:
            Transcribed text as string
        """
        return response_data.get("transcription", "")

    async def _websocket_transcribe(
        self,
        audio_data: bytes,
        model_name: str = config.DEFAULT_MODEL,
        input_format: str = config.DEFAULT_FORMAT,
    ) -> STTResult:
        """Transcribe audio using WebSocket connection.

        Args:
            audio_data: Raw audio bytes to transcribe
            model_name: Model name (default: 'default')
            input_format: Audio format (pcm, wav, opus)

        Returns:
            STTResult with transcription and metadata
        """
        headers = {config.AUTH_HEADER_NAME: self.api_key.get_secret_value()}

        segments: list[TranscriptionSegment] = []
        vad_steps: list[VADStep] = []
        request_id: str | None = None
        sample_rate: int | None = None
        frame_size: int | None = None

        logger.info(f"Connecting to STT WebSocket: {self._ws_url}")
        try:
            async with websockets.connect(self._ws_url, additional_headers=headers) as websocket:
                logger.info("WebSocket connected successfully")

                # Send setup message (must be first)
                setup_msg = {
                    "type": config.WS_MSG_SETUP,
                    "model_name": model_name,
                    "input_format": input_format,
                }
                logger.info(f"Sending setup message: {setup_msg}")
                await websocket.send(json.dumps(setup_msg))

                # Wait for ready message
                ready_msg = await websocket.recv()
                logger.info(f"Received ready message: {ready_msg[:200]}")
                ready_data = json.loads(ready_msg)

                if ready_data.get("type") != config.WS_MSG_READY:
                    msg = f"Expected ready message, got: {ready_data}"
                    raise ValueError(msg)

                request_id = ready_data.get("request_id")
                sample_rate = ready_data.get("sample_rate")
                frame_size = ready_data.get("frame_size")
                logger.info(f"Ready: request_id={request_id}, sample_rate={sample_rate}, frame_size={frame_size}")

                # Send audio in chunks
                chunk_size = config.PCM_CHUNK_SIZE * 2  # 1920 samples * 2 bytes per sample (16-bit)
                total_chunks = (len(audio_data) + chunk_size - 1) // chunk_size

                logger.info(f"Sending {total_chunks} audio chunks...")
                for i in range(0, len(audio_data), chunk_size):
                    chunk = audio_data[i:i + chunk_size]
                    audio_b64 = base64.b64encode(chunk).decode("utf-8")
                    audio_msg = {
                        "type": config.WS_MSG_AUDIO,
                        "audio": audio_b64,
                    }
                    await websocket.send(json.dumps(audio_msg))

                    # Process any incoming messages while sending (non-blocking)
                    try:
                        while True:
                            message = await asyncio.wait_for(websocket.recv(), timeout=0.001)
                            self._process_message(message, segments, vad_steps)
                    except asyncio.TimeoutError:
                        pass

                logger.info("All audio chunks sent")

                # Send end_of_stream to signal we're done
                logger.info("Sending end_of_stream")
                await websocket.send(json.dumps({"type": config.WS_MSG_END_OF_STREAM}))

                # Receive remaining messages until server sends end_of_stream
                logger.info("Receiving final messages...")
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    msg_type = data.get("type")

                    logger.info(f"Received message type: {msg_type}")

                    if msg_type == config.WS_MSG_END_OF_STREAM:
                        logger.info("Received end_of_stream from server")
                        break

                    self._process_message(message, segments, vad_steps)

        except websockets.exceptions.WebSocketException as e:
            msg = f"WebSocket connection error: {e}"
            raise RuntimeError(msg) from e

        # Build full transcription from segments
        transcription = " ".join(seg.text for seg in segments)

        logger.info(f"Transcription complete: {len(segments)} segments, {len(transcription)} characters")

        return STTResult(
            transcription=transcription,
            segments=segments,
            vad_steps=vad_steps,
            request_id=request_id,
            sample_rate=sample_rate,
            frame_size=frame_size,
        )

    def _process_message(
        self,
        message: str,
        segments: list[TranscriptionSegment],
        vad_steps: list[VADStep],
    ) -> None:
        """Process a WebSocket message and update segments/VAD.

        Args:
            message: JSON message from server
            segments: List to append transcription segments
            vad_steps: List to append VAD steps
        """
        data = json.loads(message)
        msg_type = data.get("type")

        if msg_type == config.WS_MSG_TEXT:
            # Transcription segment
            text = data.get("text", "")
            start_s = data.get("start_s", 0.0)
            stream_id = data.get("stream_id")

            segment = TranscriptionSegment(
                text=text,
                start_s=start_s,
                stream_id=stream_id,
            )
            segments.append(segment)
            logger.info(f"Received text segment: '{text}' at {start_s:.2f}s")

        elif msg_type == config.WS_MSG_END_TEXT:
            # End of text segment with stop timestamp
            stop_s = data.get("stop_s")
            stream_id = data.get("stream_id")

            # Update last segment with stop time
            if segments:
                last_segment = segments[-1]
                if last_segment.stream_id == stream_id:
                    last_segment.stop_s = stop_s
                    logger.info(f"Updated segment stop time: {stop_s:.2f}s")

        elif msg_type == config.WS_MSG_STEP:
            # VAD step
            vad_data = data.get("vad", [])
            vad_predictions = [
                VADPrediction(
                    horizon_s=v.get("horizon_s", 0.0),
                    inactivity_prob=v.get("inactivity_prob", 0.0),
                )
                for v in vad_data
            ]

            vad_step = VADStep(
                vad=vad_predictions,
                step_idx=data.get("step_idx", 0),
                step_duration_s=data.get("step_duration_s", 0.08),
                total_duration_s=data.get("total_duration_s", 0.0),
            )
            vad_steps.append(vad_step)

        elif msg_type == config.WS_MSG_ERROR:
            error_msg = data.get("message", "Unknown error")
            error_code = data.get("code")
            logger.error(f"WebSocket error (code {error_code}): {error_msg}")
            raise RuntimeError(f"WebSocket error (code {error_code}): {error_msg}")

    async def transcribe(
        self,
        *args: bytes,
        **parameters: Unpack[AudioRecognitionParameters],
    ) -> AudioRecognitionOutput:
        """Transcribe audio to text.

        Args:
            audio: Audio data as bytes (required)
            input_format: Audio format (pcm, wav, opus), default 'pcm'

        Returns:
            AudioRecognitionOutput with transcribed text
        """
        inputs = self._create_inputs(*args, **parameters)
        inputs, parameters = self._validate_artifacts(inputs, **parameters)
        request_body = self._build_request(inputs, **parameters)

        # Extract parameters
        model_name = self.model.id if self.model else config.DEFAULT_MODEL
        input_format = request_body.get("input_format", config.DEFAULT_FORMAT)

        logger.info(f"Transcribing audio with Gradium (format: {input_format})")

        # Transcribe via WebSocket
        result = await self._websocket_transcribe(
            audio_data=inputs.audio,
            model_name=model_name,
            input_format=input_format,
        )

        # Build metadata
        metadata = {
            "request_id": result.request_id,
            "sample_rate": result.sample_rate,
            "frame_size": result.frame_size,
            "region": self.region,
            "segments": [seg.model_dump() for seg in result.segments],
            "vad_steps": [step.model_dump() for step in result.vad_steps],
        }

        # Calculate usage
        characters = len(result.transcription)
        duration_s = result.vad_steps[-1].total_duration_s if result.vad_steps else None

        return self._output_class()(
            content=result.transcription,
            usage=AudioRecognitionUsage(characters=characters, duration_s=duration_s),
            metadata=metadata,
        )

    async def transcribe_stream(
        self,
        audio_stream: AsyncGenerator[bytes, None],
        **parameters: Unpack[AudioRecognitionParameters],
    ) -> AsyncGenerator[AudioRecognitionChunk, None]:
        """Stream audio to Gradium and receive real-time transcription chunks.

        Args:
            audio_stream: Async generator yielding audio chunks (PCM 24kHz recommended)
            **parameters: Additional recognition parameters (input_format, etc.)

        Yields:
            AudioRecognitionChunk: Text chunks as they are transcribed in real-time

        Example:
            ```python
            async def audio_generator():
                # Read audio in chunks
                with open("audio.wav", "rb") as f:
                    while chunk := f.read(3840):  # 1920 samples * 2 bytes
                        yield chunk

            client = create_client(...)
            async for chunk in client.transcribe_stream(audio_generator(), input_format="pcm"):
                print(f"[{chunk.start_s:.2f}s] {chunk.content}")
            ```
        """
        # Extract parameters
        model_name = self.model.id if self.model else config.DEFAULT_MODEL
        input_format = parameters.get("input_format", config.DEFAULT_FORMAT)

        headers = {config.AUTH_HEADER_NAME: self.api_key.get_secret_value()}

        logger.info(f"Starting STT streaming with format: {input_format}")

        try:
            async with websockets.connect(self._ws_url, additional_headers=headers) as websocket:
                logger.info("WebSocket connected for streaming")

                # Send setup message
                setup_msg = {
                    "type": config.WS_MSG_SETUP,
                    "model_name": model_name,
                    "input_format": input_format,
                }
                logger.info(f"Sending setup: {setup_msg}")
                await websocket.send(json.dumps(setup_msg))

                # Wait for ready
                ready_msg = await websocket.recv()
                ready_data = json.loads(ready_msg)
                if ready_data.get("type") != config.WS_MSG_READY:
                    msg = f"Expected ready message, got: {ready_data}"
                    raise ValueError(msg)

                request_id = ready_data.get("request_id")
                sample_rate = ready_data.get("sample_rate")
                logger.info(f"Ready for streaming: request_id={request_id}, sample_rate={sample_rate}")

                # Start sender task
                send_task = asyncio.create_task(
                    self._stream_audio_sender(websocket, audio_stream)
                )

                try:
                    # Receive and yield chunks
                    while True:
                        message = await websocket.recv()
                        data = json.loads(message)
                        msg_type = data.get("type")

                        if msg_type == config.WS_MSG_END_OF_STREAM:
                            logger.info("Received end_of_stream from server")
                            break

                        elif msg_type == config.WS_MSG_TEXT:
                            # Yield text chunk immediately
                            text = data.get("text", "")
                            start_s = data.get("start_s", 0.0)
                            stream_id = data.get("stream_id")

                            yield AudioRecognitionChunk(
                                content=text,
                                start_s=start_s,
                                stream_id=stream_id,
                            )
                            logger.info(f"Yielded chunk: '{text}' at {start_s:.2f}s")

                        elif msg_type == config.WS_MSG_END_TEXT:
                            # Log segment end
                            logger.debug(f"Segment ended at {data.get('stop_s')}s")

                        elif msg_type == config.WS_MSG_STEP:
                            # VAD step - just log
                            logger.debug("VAD step received")

                        elif msg_type == config.WS_MSG_ERROR:
                            error_msg = data.get("message", "Unknown error")
                            error_code = data.get("code")
                            logger.error(f"WebSocket error (code {error_code}): {error_msg}")
                            raise RuntimeError(f"WebSocket error (code {error_code}): {error_msg}")

                    # Wait for sender to complete
                    await send_task

                except Exception as e:
                    logger.error(f"Streaming error: {e}")
                    send_task.cancel()
                    raise

        except websockets.exceptions.WebSocketException as e:
            msg = f"WebSocket streaming error: {e}"
            raise RuntimeError(msg) from e

    async def _stream_audio_sender(
        self,
        websocket: websockets.WebSocketClientProtocol,
        audio_stream: AsyncGenerator[bytes, None],
    ) -> None:
        """Send audio chunks from stream to WebSocket.

        Args:
            websocket: Connected WebSocket
            audio_stream: Generator of audio bytes
        """
        try:
            async for audio_chunk in audio_stream:
                # Encode and send audio
                audio_b64 = base64.b64encode(audio_chunk).decode("utf-8")
                audio_msg = {
                    "type": config.WS_MSG_AUDIO,
                    "audio": audio_b64,
                }
                await websocket.send(json.dumps(audio_msg))
                logger.debug(f"Sent audio chunk: {len(audio_chunk)} bytes")

            # Send end of stream
            logger.info("Audio stream ended, sending end_of_stream")
            await websocket.send(json.dumps({"type": config.WS_MSG_END_OF_STREAM}))

        except Exception as e:
            logger.error(f"Error sending audio: {e}")
            raise


    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[AudioRecognitionParameters],
    ) -> httpx.Response:
        """Make HTTP request and return response object.

        Note: Overridden by transcribe() for Gradium WebSocket-based STT.
        """
        msg = "Use transcribe() or transcribe_stream() for Gradium STT (WebSocket-based)"
        raise NotImplementedError(msg)


__all__ = ["GradiumAudioRecognitionClient"]
