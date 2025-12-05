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
    MusicGenerationUsage,
)
from celeste_music_generation.parameters import MusicGenerationParameters

from . import config
from .parameters import MUREKA_PARAMETER_MAPPERS
from .polling import poll_task

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

    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[MusicGenerationParameters],
    ) -> httpx.Response:
        """Make HTTP request(s) and return response object.

        For Mureka:
        1. POST to generate endpoint -> get task_id
        2. Poll query endpoint until task completes
        3. Return final response as httpx.Response
        """
        headers = {
            config.AUTH_HEADER_NAME: f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}",
            "Content-Type": ApplicationMimeType.JSON,
        }

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

        # Step 1: Initiate generation
        logger.debug(f"Initiating Mureka generation: {request_body}")
        init_response = await self.http_client.post(
            f"{config.BASE_URL}{generate_endpoint}",
            headers=headers,
            json_body=request_body,
        )
        init_response.raise_for_status()
        init_data = init_response.json()

        task_id = init_data.get("task_id")
        if not task_id:
            msg = "No task_id in Mureka response"
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

        # Step 3: Return as httpx.Response
        # Create a mock response with the final data
        return httpx.Response(
            status_code=200,
            json=final_data,
            request=init_response.request,
        )


__all__ = ["MurekaMusicGenerationClient"]
