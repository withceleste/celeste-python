"""Gradium client implementation for speech generation."""

from typing import Any, Unpack

import httpx
from celeste_gradium.text_to_speech.client import GradiumTextToSpeechClient

from celeste.artifacts import AudioArtifact
from celeste.parameters import ParameterMapper
from celeste_speech_generation.client import SpeechGenerationClient
from celeste_speech_generation.io import (
    SpeechGenerationInput,
    SpeechGenerationOutput,
    SpeechGenerationUsage,
)
from celeste_speech_generation.parameters import SpeechGenerationParameters

from .parameters import GRADIUM_PARAMETER_MAPPERS


class GradiumSpeechGenerationClient(GradiumTextToSpeechClient, SpeechGenerationClient):
    """Gradium client for speech generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return GRADIUM_PARAMETER_MAPPERS

    def _init_request(self, inputs: SpeechGenerationInput) -> dict[str, Any]:
        """Initialize request from Gradium API format."""
        return {"text": inputs.text}

    def _parse_usage(self, response_data: dict[str, Any]) -> SpeechGenerationUsage:
        """Parse usage from response."""
        usage = super()._parse_usage(response_data)
        return SpeechGenerationUsage(**usage)

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[SpeechGenerationParameters],
    ) -> AudioArtifact:
        """Parse content from response.

        Note: This method is not used for Gradium TTS since we override generate()
        to handle WebSocket responses. Kept for interface compliance.
        """
        msg = "Gradium TTS uses WebSocket, use generate() override"
        raise NotImplementedError(msg)

    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[SpeechGenerationParameters],
    ) -> httpx.Response:
        """Make HTTP request.

        Note: This method is not used for Gradium TTS since we override generate()
        to use WebSocket. Kept for interface compliance.
        """
        msg = "Gradium TTS uses WebSocket, use generate() override"
        raise NotImplementedError(msg)

    async def generate(
        self,
        *args: str,
        **parameters: Unpack[SpeechGenerationParameters],
    ) -> SpeechGenerationOutput:
        """Generate speech from text.

        Override base generate() to use WebSocket instead of HTTP.
        """
        inputs = self._create_inputs(*args, **parameters)
        inputs, parameters = self._validate_artifacts(inputs, **parameters)
        request_body = self._build_request(inputs, **parameters)

        # Use WebSocket TTS flow
        audio_bytes, output_format = await self._websocket_tts(request_body)

        if not audio_bytes:
            msg = "No audio data in response"
            raise ValueError(msg)

        # Determine MIME type from output_format
        mime_type = self._map_output_format_to_mime_type(output_format)

        return self._output_class()(
            content=AudioArtifact(data=audio_bytes, mime_type=mime_type),
            usage=SpeechGenerationUsage(),
            metadata=self._build_metadata({}),
        )


__all__ = ["GradiumSpeechGenerationClient"]
