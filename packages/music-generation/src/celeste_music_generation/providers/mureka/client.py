"""Mureka client implementation for music generation."""

import logging
from typing import Any, Unpack

import httpx

from celeste.artifacts import AudioArtifact
from celeste.mime_types import ApplicationMimeType
from celeste.parameters import ParameterMapper
from celeste_music_generation.client import MusicGenerationClient
from celeste_music_generation.io import (
    MusicGenerationFinishReason,
    MusicGenerationInput,
    MusicGenerationOutput,
    MusicGenerationUsage,
)
from celeste_music_generation.parameters import MusicGenerationParameters

from . import config
from .exceptions import raise_mureka_error
from .parameters import MUREKA_PARAMETER_MAPPERS
from .polling import poll_task
from .types import BillingInfo, LyricsOutput, SongDescription, StemOutput

logger = logging.getLogger(__name__)


class MurekaMusicGenerationClient(MusicGenerationClient):
    """Mureka client for music generation.

    Uses Mureka's async task-based API:
    1. POST /v1/song/generate returns task_id
    2. Poll GET /v1/song/query/{task_id} until succeeded
    3. Extract audio URL from final result
    """

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return MUREKA_PARAMETER_MAPPERS

    def _init_request(self, inputs: MusicGenerationInput) -> dict[str, Any]:
        """Initialize request for Mureka API format."""
        # Use model ID as the model parameter
        # Note: Do NOT include empty lyrics - only add via parameter mapper if non-empty
        request: dict[str, Any] = {
            "model": self.model.id,
            "prompt": inputs.prompt,
        }
        return request

    def _parse_usage(self, response_data: dict[str, Any]) -> MusicGenerationUsage:
        """Parse usage from Mureka response."""
        usage_data = response_data.get("usage", {})
        return MusicGenerationUsage(
            total_tokens=usage_data.get("total_tokens"),
            credits_used=usage_data.get("credits"),
            billed_units=usage_data.get("billed_units"),
        )

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[MusicGenerationParameters],
    ) -> AudioArtifact:
        """Parse audio content from Mureka response.

        Mureka returns audio URLs in the 'choices' array or 'stream_url' for streaming.
        """
        # Check for stream_url (streaming case)
        stream_url = response_data.get("stream_url")
        if stream_url:
            return AudioArtifact(url=stream_url)

        # Check for choices (standard case)
        choices = response_data.get("choices", [])
        if not choices:
            msg = "No audio data in response"
            raise ValueError(msg)

        # Get first choice
        choice = choices[0]
        audio_url = choice.get("audio_url") or choice.get("url")

        if not audio_url:
            msg = "No audio URL in response choice"
            raise ValueError(msg)

        return AudioArtifact(url=audio_url)

    def _parse_finish_reason(
        self, response_data: dict[str, Any]
    ) -> MusicGenerationFinishReason | None:
        """Parse finish reason from Mureka response."""
        status = response_data.get("status")
        if not status:
            return None

        return MusicGenerationFinishReason(
            reason=status,
            message=response_data.get("error"),
        )

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary from response data."""
        metadata = super()._build_metadata(response_data)

        # Add Mureka-specific fields
        if "task_id" in response_data:
            metadata["task_id"] = response_data["task_id"]
        if "trace_id" in response_data:
            metadata["trace_id"] = response_data["trace_id"]
        if "duration" in response_data:
            metadata["duration"] = response_data["duration"]

        return metadata

    async def generate(
        self,
        *args: str,
        **parameters: Unpack[MusicGenerationParameters],
    ) -> MusicGenerationOutput:
        """Generate music from text prompt.

        Override base generate() to handle Mureka's async task-based API.
        """
        inputs = self._create_inputs(*args, **parameters)
        inputs, parameters = self._validate_artifacts(inputs, **parameters)
        request_body = self._build_request(inputs, **parameters)

        # Determine endpoint based on instrumental_only parameter
        instrumental_only = parameters.get("instrumental_only", False)
        generate_endpoint = (
            config.INSTRUMENTAL_GENERATE_ENDPOINT
            if instrumental_only
            else config.SONG_GENERATE_ENDPOINT
        )
        query_endpoint = (
            config.INSTRUMENTAL_QUERY_ENDPOINT
            if instrumental_only
            else config.SONG_QUERY_ENDPOINT
        )

        # Clean request body for instrumental endpoint
        if instrumental_only:
            # Instrumental endpoint does not support these fields
            request_body.pop("lyrics", None)
            request_body.pop("vocal_id", None)
            request_body.pop("reference_id", None)
            # Keep: model, prompt, n, instrumental_id, stream

        headers = {
            config.AUTH_HEADER_NAME: f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}",
            "Content-Type": str(ApplicationMimeType.JSON),
        }

        # Step 1: Initiate generation
        logger.info(f"Mureka API Request - Endpoint: {config.BASE_URL}{generate_endpoint}")
        logger.info(f"Mureka API Request - Headers: {headers}")
        logger.info(f"Mureka API Request - Body: {request_body}")
        init_response = await self.http_client.post(
            f"{config.BASE_URL}{generate_endpoint}",
            headers=headers,
            json_body=request_body,
        )

        # Log response for debugging
        logger.info(f"Mureka API Response - Status: {init_response.status_code}")

        # Handle errors with detailed Mureka exceptions
        if init_response.status_code >= 400:
            try:
                error_data = init_response.json()
                logger.error(f"Mureka API Error - Body: {error_data}")
                error_info = error_data.get("error", {})
                error_message = error_info.get("message", "Unknown error")
                trace_id = error_data.get("trace_id")
                raise_mureka_error(init_response.status_code, error_message, trace_id)
            except ValueError:
                # Response is not JSON
                logger.error(f"Mureka API Error - Text: {init_response.text}")
                init_response.raise_for_status()

        init_data = init_response.json()
        logger.info(f"Mureka API Response - Body: {init_data}")

        # Mureka returns 'id' not 'task_id'
        task_id = init_data.get("id")
        if not task_id:
            msg = "No task ID in Mureka response"
            raise ValueError(msg)

        logger.info(f"Mureka task created: {task_id}")

        # Step 2: Poll until completion
        auth_header = f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}"
        final_data = await poll_task(
            http_client=self.http_client,
            task_id=task_id,
            query_endpoint=query_endpoint,
            auth_header=auth_header,
        )

        # Step 3: Parse response and return output
        return self._output_class()(
            content=self._parse_content(final_data, **parameters),
            usage=self._parse_usage(final_data),
            finish_reason=self._parse_finish_reason(final_data),
            metadata=self._build_metadata(final_data),
        )

    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[MusicGenerationParameters],
    ) -> httpx.Response:
        """Make HTTP request(s) and return response object.

        Note: This method is not used for Mureka since we override generate().
        Kept for interface compliance.
        """
        msg = "Mureka uses async task-based API, use generate() override"
        raise NotImplementedError(msg)

    # Extended Mureka-specific methods

    async def generate_lyrics(self, prompt: str) -> LyricsOutput:
        """Generate lyrics from a prompt.

        Args:
            prompt: Description of the desired lyrics theme/content

        Returns:
            LyricsOutput with title and lyrics
        """
        headers = {
            config.AUTH_HEADER_NAME: f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}",
            "Content-Type": str(ApplicationMimeType.JSON),
        }

        request_body = {"prompt": prompt}

        logger.info(f"Generating lyrics with prompt: {prompt[:50]}...")
        response = await self.http_client.post(
            f"{config.BASE_URL}/v1/lyrics/generate",
            headers=headers,
            json_body=request_body,
        )

        if response.status_code >= 400:
            try:
                error_data = response.json()
                error_info = error_data.get("error", {})
                error_message = error_info.get("message", "Unknown error")
                trace_id = error_data.get("trace_id")
                raise_mureka_error(response.status_code, error_message, trace_id)
            except ValueError:
                response.raise_for_status()

        data = response.json()
        return LyricsOutput(**data)

    async def extend_lyrics(self, lyrics: str) -> LyricsOutput:
        """Extend existing lyrics.

        Args:
            lyrics: Existing lyrics to continue from

        Returns:
            LyricsOutput with extended lyrics
        """
        headers = {
            config.AUTH_HEADER_NAME: f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}",
            "Content-Type": str(ApplicationMimeType.JSON),
        }

        request_body = {"lyrics": lyrics}

        logger.info(f"Extending lyrics ({len(lyrics)} characters)...")
        response = await self.http_client.post(
            f"{config.BASE_URL}/v1/lyrics/extend",
            headers=headers,
            json_body=request_body,
        )

        if response.status_code >= 400:
            try:
                error_data = response.json()
                error_info = error_data.get("error", {})
                error_message = error_info.get("message", "Unknown error")
                trace_id = error_data.get("trace_id")
                raise_mureka_error(response.status_code, error_message, trace_id)
            except ValueError:
                response.raise_for_status()

        data = response.json()
        return LyricsOutput(**data)

    async def extend_song(
        self,
        lyrics: str,
        extend_at: int,
        song_id: str | None = None,
        upload_audio_id: str | None = None,
    ) -> MusicGenerationOutput:
        """Extend an existing song with additional lyrics.

        Args:
            lyrics: New lyrics to add
            extend_at: Start time in milliseconds [8000, 420000]
            song_id: Song ID from song/generate (mutually exclusive with upload_audio_id)
            upload_audio_id: Upload ID from files/upload (mutually exclusive with song_id)

        Returns:
            MusicGenerationOutput with extended song

        Raises:
            ValueError: If both or neither song_id/upload_audio_id are provided
        """
        if (song_id is None) == (upload_audio_id is None):
            msg = "Must provide exactly one of song_id or upload_audio_id"
            raise ValueError(msg)

        if not 8000 <= extend_at <= 420000:
            msg = f"extend_at must be in range [8000, 420000], got {extend_at}"
            raise ValueError(msg)

        headers = {
            config.AUTH_HEADER_NAME: f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}",
            "Content-Type": str(ApplicationMimeType.JSON),
        }

        request_body: dict[str, Any] = {
            "lyrics": lyrics,
            "extend_at": extend_at,
        }

        if song_id:
            request_body["song_id"] = song_id
        else:
            request_body["upload_audio_id"] = upload_audio_id

        logger.info(f"Extending song at {extend_at}ms...")
        init_response = await self.http_client.post(
            f"{config.BASE_URL}/v1/song/extend",
            headers=headers,
            json_body=request_body,
        )

        if init_response.status_code >= 400:
            try:
                error_data = init_response.json()
                error_info = error_data.get("error", {})
                error_message = error_info.get("message", "Unknown error")
                trace_id = error_data.get("trace_id")
                raise_mureka_error(init_response.status_code, error_message, trace_id)
            except ValueError:
                init_response.raise_for_status()

        init_data = init_response.json()
        task_id = init_data.get("id")
        if not task_id:
            msg = "No task ID in Mureka response"
            raise ValueError(msg)

        logger.info(f"Extend task created: {task_id}")

        # Poll until completion
        auth_header = f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}"
        final_data = await poll_task(
            http_client=self.http_client,
            task_id=task_id,
            query_endpoint=config.SONG_QUERY_ENDPOINT,
            auth_header=auth_header,
        )

        # Parse response
        return self._output_class()(
            content=self._parse_content(final_data),
            usage=self._parse_usage(final_data),
            finish_reason=self._parse_finish_reason(final_data),
            metadata=self._build_metadata(final_data),
        )

    async def describe_song(self, url: str) -> SongDescription:
        """Analyze and describe a song's characteristics.

        Args:
            url: URL of the song (http/https) or base64 data URL
                 Supported formats: mp3, m4a (max 10MB for base64)

        Returns:
            SongDescription with instruments, genres, tags, description
        """
        headers = {
            config.AUTH_HEADER_NAME: f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}",
            "Content-Type": str(ApplicationMimeType.JSON),
        }

        request_body = {"url": url}

        logger.info("Describing song...")
        response = await self.http_client.post(
            f"{config.BASE_URL}/v1/song/describe",
            headers=headers,
            json_body=request_body,
        )

        if response.status_code >= 400:
            try:
                error_data = response.json()
                error_info = error_data.get("error", {})
                error_message = error_info.get("message", "Unknown error")
                trace_id = error_data.get("trace_id")
                raise_mureka_error(response.status_code, error_message, trace_id)
            except ValueError:
                response.raise_for_status()

        data = response.json()
        return SongDescription(
            instruments=data.get("instrument", []),
            genres=data.get("genres", []),
            tags=data.get("tags", []),
            description=data.get("description", ""),
        )

    async def stem_song(self, url: str) -> StemOutput:
        """Separate a song into individual tracks (stems).

        Args:
            url: URL of the song (http/https) or base64 data URL
                 Supported formats: mp3, m4a (max 10MB for base64)

        Returns:
            StemOutput with zip_url containing all separated tracks
        """
        headers = {
            config.AUTH_HEADER_NAME: f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}",
            "Content-Type": str(ApplicationMimeType.JSON),
        }

        request_body = {"url": url}

        logger.info("Stemming song (separating tracks)...")
        response = await self.http_client.post(
            f"{config.BASE_URL}/v1/song/stem",
            headers=headers,
            json_body=request_body,
        )

        if response.status_code >= 400:
            try:
                error_data = response.json()
                error_info = error_data.get("error", {})
                error_message = error_info.get("message", "Unknown error")
                trace_id = error_data.get("trace_id")
                raise_mureka_error(response.status_code, error_message, trace_id)
            except ValueError:
                response.raise_for_status()

        data = response.json()
        return StemOutput(**data)

    async def get_billing(self) -> BillingInfo:
        """Get account billing information.

        Returns:
            BillingInfo with account balance, spending, and limits
        """
        headers = {
            config.AUTH_HEADER_NAME: f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}",
        }

        logger.info("Fetching billing information...")
        response = await self.http_client.get(
            f"{config.BASE_URL}/v1/account/billing",
            headers=headers,
        )

        if response.status_code >= 400:
            try:
                error_data = response.json()
                error_info = error_data.get("error", {})
                error_message = error_info.get("message", "Unknown error")
                trace_id = error_data.get("trace_id")
                raise_mureka_error(response.status_code, error_message, trace_id)
            except ValueError:
                response.raise_for_status()

        data = response.json()
        return BillingInfo(**data)


__all__ = ["MurekaMusicGenerationClient"]
