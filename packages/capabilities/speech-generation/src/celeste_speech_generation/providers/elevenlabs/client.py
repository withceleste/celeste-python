"""ElevenLabs client implementation for speech generation."""

from typing import Any, Unpack

from celeste_elevenlabs.text_to_speech.client import ElevenLabsTextToSpeechClient

from celeste.artifacts import AudioArtifact
from celeste.parameters import ParameterMapper
from celeste_speech_generation.client import SpeechGenerationClient
from celeste_speech_generation.io import (
    SpeechGenerationInput,
    SpeechGenerationOutput,
    SpeechGenerationUsage,
)
from celeste_speech_generation.parameters import (
    SpeechGenerationParameter,
    SpeechGenerationParameters,
)

from .parameters import ELEVENLABS_PARAMETER_MAPPERS
from .streaming import ElevenLabsSpeechGenerationStream


class ElevenLabsSpeechGenerationClient(
    ElevenLabsTextToSpeechClient, SpeechGenerationClient
):
    """ElevenLabs client for speech generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return ELEVENLABS_PARAMETER_MAPPERS

    def _init_request(self, inputs: SpeechGenerationInput) -> dict[str, Any]:
        """Initialize request from ElevenLabs API format."""
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

        Note: This method is not used for ElevenLabs TTS since we override generate()
        to handle binary responses. Kept for interface compliance.
        """
        # This should never be called for ElevenLabs TTS
        msg = "ElevenLabs TTS returns binary responses, use generate() override"
        raise NotImplementedError(msg)

    async def generate(
        self,
        *args: str,
        **parameters: Unpack[SpeechGenerationParameters],
    ) -> SpeechGenerationOutput:
        """Generate speech from text.

        Override base generate() to handle binary audio response from ElevenLabs TTS.
        """
        inputs = self._create_inputs(*args, **parameters)
        inputs, parameters = self._validate_artifacts(inputs, **parameters)
        request_body = self._build_request(inputs, **parameters)
        response = await self._make_request(request_body, **parameters)
        self._handle_error_response(response)

        # Handle binary response (ElevenLabs TTS returns raw audio bytes, not JSON)
        audio_bytes = response.content
        if not audio_bytes:
            msg = "No audio data in response"
            raise ValueError(msg)

        # Determine MIME type from output_format parameter
        output_format = (
            parameters.get(SpeechGenerationParameter.OUTPUT_FORMAT) or "mp3_44100_128"
        )
        mime_type = self._map_output_format_to_mime_type(output_format)

        # Extract headers from response (ElevenLabs returns metadata like request-id in headers)
        headers_dict = dict(response.headers)

        return self._output_class()(
            content=AudioArtifact(data=audio_bytes, mime_type=mime_type),
            usage=SpeechGenerationUsage(),
            metadata=self._build_metadata(headers_dict),
        )

    def _stream_class(self) -> type[ElevenLabsSpeechGenerationStream]:
        """Return the Stream class for this client."""
        return ElevenLabsSpeechGenerationStream


__all__ = ["ElevenLabsSpeechGenerationClient"]
