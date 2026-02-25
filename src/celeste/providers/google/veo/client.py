"""Google Veo API client mixin."""

import asyncio
import logging
from collections.abc import AsyncIterator
from typing import Any, ClassVar

from celeste.client import APIMixin
from celeste.exceptions import StreamingNotSupportedError
from celeste.io import FinishReason

from ..auth import GoogleADC
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

    _content_fields: ClassVar[set[str]] = {"response"}

    def _get_vertex_endpoint(self, gemini_endpoint: str) -> str:
        """Map Gemini Veo endpoint to Vertex AI endpoint."""
        mapping: dict[str, str] = {
            config.GoogleVeoEndpoint.CREATE_VIDEO: config.VertexVeoEndpoint.CREATE_VIDEO,
        }
        vertex_endpoint = mapping.get(gemini_endpoint)
        if vertex_endpoint is None:
            raise ValueError(f"No Vertex AI endpoint mapping for: {gemini_endpoint}")
        return vertex_endpoint

    def _build_url(self, endpoint: str) -> str:
        """Build full URL based on auth type."""
        if isinstance(self.auth, GoogleADC):
            return self.auth.build_url(
                self._get_vertex_endpoint(endpoint), model_id=self.model.id
            )
        return f"{config.BASE_URL}{endpoint.format(model_id=self.model.id)}"

    def _build_poll_url(self, operation_name: str) -> str:
        """Build polling URL for long-running operations."""
        if isinstance(self.auth, GoogleADC):
            return self.auth.build_url(
                config.VertexVeoEndpoint.FETCH_OPERATION, model_id=self.model.id
            )
        poll_path = config.GoogleVeoEndpoint.GET_OPERATION.format(
            operation_name=operation_name
        )
        return f"{config.BASE_URL}{poll_path}"

    async def _make_poll_request(
        self, operation_name: str, extra_headers: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """Poll a long-running operation.

        Vertex AI uses POST to fetchPredictOperation with operationName in body.
        AI Studio uses GET to /v1beta/{operation_name}.
        """
        headers = self._json_headers(extra_headers)
        poll_url = self._build_poll_url(operation_name)

        if isinstance(self.auth, GoogleADC):
            response = await self.http_client.post(
                poll_url,
                headers=headers,
                json_body={"operationName": operation_name},
                timeout=config.DEFAULT_TIMEOUT,
            )
        else:
            response = await self.http_client.get(
                poll_url,
                headers=headers,
                timeout=config.DEFAULT_TIMEOUT,
            )

        self._handle_error_response(response)
        data: dict[str, Any] = response.json()
        return data

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """Veo API does not support SSE streaming in this client."""
        raise StreamingNotSupportedError(model_id=self.model.id)

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Make HTTP request with async polling for Veo video generation."""
        if endpoint is None:
            endpoint = config.GoogleVeoEndpoint.CREATE_VIDEO

        headers = self._json_headers(extra_headers)

        logger.info(f"Initiating video generation with model {self.model.id}")
        response = await self.http_client.post(
            self._build_url(endpoint),
            headers=headers,
            json_body=request_body,
            timeout=config.DEFAULT_TIMEOUT,
        )

        self._handle_error_response(response)
        operation_data: dict[str, Any] = response.json()

        operation_name = operation_data["name"]
        logger.info(f"Video generation started: {operation_name}")

        while True:
            await asyncio.sleep(config.POLL_INTERVAL)
            logger.debug(f"Polling operation status: {operation_name}")

            operation_data = await self._make_poll_request(
                operation_name, extra_headers=extra_headers
            )

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
        response = response_data.get("response", {})

        if isinstance(self.auth, GoogleADC):
            videos = response.get("videos", [])
            if not videos:
                msg = "No videos in response"
                raise ValueError(msg)
            video = videos[0]
            # Normalize Vertex key "videoGcsUri" to "uri" for consistency
            if "videoGcsUri" in video:
                video["uri"] = video.pop("videoGcsUri")
            return video

        generated_samples = response.get("generateVideoResponse", {}).get(
            "generatedSamples", []
        )
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
