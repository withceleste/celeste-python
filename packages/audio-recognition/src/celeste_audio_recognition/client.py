"""Base client for audio recognition."""

from abc import abstractmethod
from typing import Any, Unpack

import httpx

from celeste.client import Client
from celeste.exceptions import ValidationError
from celeste_audio_recognition.io import (
    AudioRecognitionInput,
    AudioRecognitionOutput,
    AudioRecognitionUsage,
)
from celeste_audio_recognition.parameters import AudioRecognitionParameters


class AudioRecognitionClient(
    Client[AudioRecognitionInput, AudioRecognitionOutput, AudioRecognitionParameters]
):
    """Client for audio recognition operations (Speech-to-Text)."""

    @abstractmethod
    def _init_request(self, inputs: AudioRecognitionInput) -> dict[str, Any]:
        """Initialize provider-specific request structure."""

    @abstractmethod
    def _parse_usage(self, response_data: dict[str, Any]) -> AudioRecognitionUsage:
        """Parse usage information from provider response."""

    @abstractmethod
    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[AudioRecognitionParameters],
    ) -> str:
        """Parse transcribed text from provider response."""

    def _create_inputs(
        self,
        *args: bytes,
        audio: bytes | None = None,
        format: str = "pcm",
        **parameters: Unpack[AudioRecognitionParameters],
    ) -> AudioRecognitionInput:
        """Map positional arguments to Input type."""
        if args:
            return AudioRecognitionInput(audio=args[0], format=format)
        if audio is None:
            msg = "audio is required (either as positional argument or keyword argument)"
            raise ValidationError(msg)
        return AudioRecognitionInput(audio=audio, format=format)

    @classmethod
    def _output_class(cls) -> type[AudioRecognitionOutput]:
        """Return the Output class for this client."""
        return AudioRecognitionOutput

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary from response data."""
        metadata = super()._build_metadata(response_data)
        metadata["raw_response"] = response_data
        return metadata

    @abstractmethod
    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[AudioRecognitionParameters],
    ) -> httpx.Response:
        """Make HTTP request(s) and return response object."""


__all__ = ["AudioRecognitionClient"]
