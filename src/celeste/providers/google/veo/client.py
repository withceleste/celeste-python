"""Google Veo API client mixin."""

import asyncio
import logging
from collections.abc import AsyncIterator
from typing import Any

from celeste.client import APIMixin
from celeste.exceptions import StreamingNotSupportedError
from celeste.io import FinishReason
from celeste.mime_types import ApplicationMimeType

from . import config

logger = logging.getLogger(__name__)


class GoogleVeoClient(APIMixin):
    """Mixin for Veo API capabilities.

    Provides shared implementation for video generation using the Veo API:
    - _make_request() - HTTP POST with async polling for long-running operations
    - _parse_content() - Extract raw video dict from response (generic)
    - download_content() - Download from GCS URL, returns raw bytes (generic)

    Capability clients extend via super() to wrap results in artifacts:
        class GoogleVideoGenerationClient(GoogleVeoClient, VideoGenerationClient):
            def _parse_content(self, response_data, **params):
                video_data = super()._parse_content(response_data)  # Get generic dict
                return VideoArtifact(url=video_data["uri"])  # Capability-specific

            async def download_content(self, artifact: VideoArtifact) -> VideoArtifact:
                video_bytes = await super().download_content(artifact.url)  # Get raw bytes
                return VideoArtifact(data=video_bytes, mime_type=VideoMimeType.MP4, ...)
    """

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        **parameters: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """Veo API does not support SSE streaming in this client."""
        raise StreamingNotSupportedError(model_id=self.model.id)

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Make HTTP request with async polling for Veo video generation."""
        if endpoint is None:
            endpoint = config.GoogleVeoEndpoint.CREATE_VIDEO
        endpoint = endpoint.format(model_id=self.model.id)
        url = f"{config.BASE_URL}{endpoint}"

        auth_headers = self.auth.get_headers()
        headers = {
            **auth_headers,
            "Content-Type": ApplicationMimeType.JSON,
        }

        logger.info(f"Initiating video generation with model {self.model.id}")
        response = await self.http_client.post(
            url,
            headers=headers,
            json_body=request_body,
            timeout=config.DEFAULT_TIMEOUT,
        )

        self._handle_error_response(response)
        operation_data: dict[str, Any] = response.json()

        operation_name = operation_data["name"]
        logger.info(f"Video generation started: {operation_name}")

        poll_url = f"{config.BASE_URL}{config.GoogleVeoEndpoint.GET_OPERATION.format(operation_name=operation_name)}"
        poll_headers = auth_headers

        while True:
            await asyncio.sleep(config.POLL_INTERVAL)
            logger.debug(f"Polling operation status: {operation_name}")

            poll_response = await self.http_client.get(
                poll_url,
                headers=poll_headers,
                timeout=config.DEFAULT_TIMEOUT,
            )

            self._handle_error_response(poll_response)
            operation_data = poll_response.json()

            if operation_data.get("done"):
                if "error" in operation_data:
                    error = operation_data["error"]
                    error_msg = error.get("message", "Unknown error")
                    error_code = error.get("code", "UNKNOWN")
                    msg = f"Video generation failed: {error_code} - {error_msg}"
                    raise ValueError(msg)

                logger.info(f"Video generation completed: {operation_name}")
                break

        return operation_data

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Extract raw video dict from response.

        Returns generic dict with video data that capability clients wrap in artifacts.
        """
        generate_response = response_data.get("response", {}).get(
            "generateVideoResponse", {}
        )
        generated_samples = generate_response.get("generatedSamples", [])
        if not generated_samples:
            msg = "No generated samples in response"
            raise ValueError(msg)
        return generated_samples[0].get("video", {})

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | float | None]:
        """Map Google Veo usage fields to unified names.

        Shared by client and streaming across all capabilities.
        Veo API doesn't provide usage metadata.
        """
        return {}

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """Extract usage data from Veo API response."""
        return GoogleVeoClient.map_usage_fields(response_data)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """Veo API doesn't provide finish reasons."""
        return FinishReason(reason=None)

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary, filtering out content fields."""
        content_fields = {"response"}
        filtered_data = {
            k: v for k, v in response_data.items() if k not in content_fields
        }
        return super()._build_metadata(filtered_data)

    async def download_content(self, url: str) -> bytes:
        """Download video content from GCS URL.

        Returns raw bytes that capability clients wrap in VideoArtifact.

        Args:
            url: GCS URL (gs://) or HTTPS URL to download from.

        Returns:
            Raw video bytes.
        """
        download_url = url
        if download_url.startswith("gs://"):
            download_url = download_url.replace("gs://", config.STORAGE_BASE_URL, 1)

        logger.info(f"Downloading video from: {download_url}")

        headers = self.auth.get_headers()

        response = await self.http_client.get(
            download_url,
            headers=headers,
            timeout=config.DEFAULT_TIMEOUT,
            follow_redirects=True,
        )

        self._handle_error_response(response)
        return response.content


__all__ = ["GoogleVeoClient"]
