"""Mureka client implementation for speech generation."""

import logging
from typing import Any, Unpack

import httpx

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
from .parameters import MUREKA_PARAMETER_MAPPERS
from .types import PodcastOutput, PodcastTurn

logger = logging.getLogger(__name__)


class MurekaSpeechGenerationClient(SpeechGenerationClient):
    """Mureka client for speech generation (TTS and podcast).

    Supports:
    - Single-voice TTS (generate method)
    - Multi-voice podcast generation (generate_podcast method)
    """

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return MUREKA_PARAMETER_MAPPERS

    def _init_request(self, inputs: SpeechGenerationInput) -> dict[str, Any]:
        """Initialize request for Mureka TTS API format."""
        request: dict[str, Any] = {
            "text": inputs.text,
        }
        return request

    def _parse_usage(self, response_data: dict[str, Any]) -> SpeechGenerationUsage:
        """Parse usage from Mureka response.

        Mureka doesn't provide usage metrics for TTS.
        """
        return SpeechGenerationUsage()

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[SpeechGenerationParameters],
    ) -> AudioArtifact:
        """Parse audio content from Mureka response.

        Mureka returns a URL to download the generated audio.
        """
        url = response_data.get("url")
        if not url:
            msg = "No audio URL in response"
            raise ValueError(msg)

        return AudioArtifact(url=url)

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary from response data."""
        metadata = super()._build_metadata(response_data)

        # Add Mureka-specific fields
        if "expires_at" in response_data:
            metadata["expires_at"] = response_data["expires_at"]

        return metadata

    async def generate(
        self,
        *args: str,
        **parameters: Unpack[SpeechGenerationParameters],
    ) -> SpeechGenerationOutput:
        """Generate speech from text.

        Args:
            text: Text to convert to speech (required)
            voice: Voice to use (required - one of Ethan, Victoria, Jake, Luna, Emma)
            voice_id: Custom voice ID (mutually exclusive with voice)

        Returns:
            SpeechGenerationOutput with audio URL
        """
        inputs = self._create_inputs(*args, **parameters)
        inputs, parameters = self._validate_artifacts(inputs, **parameters)
        request_body = self._build_request(inputs, **parameters)

        # Add voice parameter
        voice = parameters.get("voice")
        voice_id = parameters.get("voice_id")

        if voice:
            request_body["voice"] = voice
        elif voice_id:
            request_body["voice_id"] = voice_id
        else:
            # Default to Emma if no voice specified
            request_body["voice"] = "Emma"

        headers = {
            config.AUTH_HEADER_NAME: f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}",
            "Content-Type": str(ApplicationMimeType.JSON),
        }

        logger.info(f"Generating speech with Mureka (voice: {request_body.get('voice') or request_body.get('voice_id')})")
        response = await self.http_client.post(
            f"{config.BASE_URL}{config.TTS_GENERATE_ENDPOINT}",
            headers=headers,
            json_body=request_body,
        )

        if response.status_code >= 400:
            response.raise_for_status()

        response_data = response.json()

        return self._output_class()(
            content=self._parse_content(response_data, **parameters),
            usage=self._parse_usage(response_data),
            metadata=self._build_metadata(response_data),
        )

    async def generate_podcast(
        self,
        conversations: list[PodcastTurn] | list[dict[str, str]],
    ) -> PodcastOutput:
        """Generate a podcast-style conversation with multiple voices.

        Args:
            conversations: List of conversation turns (max 10)
                Each turn must have:
                - text: The text to speak
                - voice: The voice to use (Ethan, Victoria, Jake, Luna, Emma)

        Returns:
            PodcastOutput with audio URL and expiration time

        Example:
            podcast = await client.generate_podcast([
                {"text": "Hello, I'm Luna", "voice": "Luna"},
                {"text": "And I'm Jake", "voice": "Jake"},
                {"text": "Welcome to our show!", "voice": "Luna"},
            ])
        """
        if len(conversations) > 10:
            msg = "Maximum 10 conversation turns allowed"
            raise ValueError(msg)

        # Convert to PodcastTurn if dict
        turns = []
        for conv in conversations:
            if isinstance(conv, dict):
                turns.append(conv)
            elif isinstance(conv, PodcastTurn):
                turns.append({"text": conv.text, "voice": conv.voice})
            else:
                msg = f"Invalid conversation turn type: {type(conv)}"
                raise TypeError(msg)

        request_body = {"conversations": turns}

        headers = {
            config.AUTH_HEADER_NAME: f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}",
            "Content-Type": str(ApplicationMimeType.JSON),
        }

        logger.info(f"Generating podcast with {len(turns)} turns")
        response = await self.http_client.post(
            f"{config.BASE_URL}{config.PODCAST_GENERATE_ENDPOINT}",
            headers=headers,
            json_body=request_body,
        )

        if response.status_code >= 400:
            response.raise_for_status()

        data = response.json()
        return PodcastOutput(**data)

    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[SpeechGenerationParameters],
    ) -> httpx.Response:
        """Make HTTP request and return response object.

        Note: Overridden by generate() for Mureka.
        """
        msg = "Use generate() or generate_podcast() for Mureka TTS"
        raise NotImplementedError(msg)


__all__ = ["MurekaSpeechGenerationClient"]
