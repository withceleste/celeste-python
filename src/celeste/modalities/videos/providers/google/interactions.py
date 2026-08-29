"""Google videos client (Interactions API — Gemini Omni)."""

import asyncio
from typing import Any, Unpack
from urllib.parse import urlsplit, urlunsplit

from celeste.artifacts import VideoArtifact
from celeste.http import DEFAULT_TIMEOUT
from celeste.mime_types import VideoMimeType
from celeste.parameters import ParameterMapper
from celeste.providers.google.auth import GoogleADC
from celeste.providers.google.interactions import config
from celeste.providers.google.interactions.client import (
    GoogleInteractionsClient as GoogleInteractionsMixin,
)
from celeste.providers.google.utils import (
    build_content_part,
    get_with_auth_safe_redirects,
)
from celeste.types import VideoContent

from ...client import VideosClient
from ...io import VideoInput
from ...parameters import VideoParameters
from .parameters import GOOGLE_INTERACTIONS_PARAMETER_MAPPERS


class GoogleInteractionsVideosClient(GoogleInteractionsMixin, VideosClient):
    """Google videos client (Interactions API)."""

    _generate_endpoint = config.GoogleInteractionsEndpoint.CREATE_INTERACTION
    _edit_endpoint = config.GoogleInteractionsEndpoint.CREATE_INTERACTION

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[VideoContent]]:
        return GOOGLE_INTERACTIONS_PARAMETER_MAPPERS

    def _init_request(self, inputs: VideoInput) -> dict[str, Any]:
        """Initialize request for Omni video generation/edit."""
        request: dict[str, Any] = {"response_format": {"type": "video"}}
        if inputs.video is None:
            request["input"] = inputs.prompt
            return request
        request["input"] = [
            build_content_part(inputs.video, "video"),
            {"type": "text", "text": inputs.prompt},
        ]
        if self.model.id == "gemini-omni-flash-preview":
            request["generation_config"] = {"video_config": {"task": "edit"}}
        return request

    def _build_request(
        self,
        inputs: VideoInput,
        extra_body: dict[str, Any] | None = None,
        streaming: bool = False,
        **parameters: Unpack[VideoParameters],
    ) -> dict[str, Any]:
        """Build a request and select URI delivery for Developer high-res video."""
        request = super()._build_request(
            inputs,
            extra_body=extra_body,
            streaming=streaming,
            **parameters,
        )
        response_format = request.get("response_format")
        if (
            not isinstance(self.auth, GoogleADC)
            and self.model.id == "gemini-omni-1.1-flash"
            and isinstance(response_format, dict)
            and response_format.get("resolution") in ("1080p", "4k")
        ):
            response_format["delivery"] = "uri"
        return request

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> VideoArtifact:
        """Parse the video artifact from the model_output step."""
        steps = super()._parse_content(response_data)
        for step in steps:
            if step.get("type") != "model_output":
                continue
            for part in step.get("content", []):
                if part.get("type") != "video":
                    continue
                mime_type = VideoMimeType(part.get("mime_type", "video/mp4"))
                if part.get("data"):
                    return VideoArtifact(data=part["data"], mime_type=mime_type)
                if part.get("uri"):
                    return VideoArtifact(url=part["uri"], mime_type=mime_type)
        msg = "No video content in response"
        raise ValueError(msg)

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[VideoParameters],
    ) -> dict[str, Any]:
        """Wait for a returned Developer File before exposing its download URI."""
        response_data = await super()._make_request(
            request_body,
            endpoint=endpoint,
            extra_headers=extra_headers,
            **parameters,
        )
        artifact = self._parse_content(response_data)
        if artifact.url is not None:
            await self._wait_until_file_active(artifact.url)
        return response_data

    async def download_content(self, artifact: VideoArtifact) -> VideoArtifact:
        """Download video content from the response URI."""
        if artifact.data is not None:
            return artifact

        if artifact.url is None:
            msg = "Artifact has no URL or data to download"
            raise ValueError(msg)

        headers = self.auth.get_headers()
        status_url = await self._wait_until_file_active(artifact.url)

        download_url = artifact.url
        if status_url is not None and not urlsplit(download_url).path.endswith(
            ":download"
        ):
            download_url = f"{status_url}:download?alt=media"
        if download_url.startswith("gs://"):
            download_url = download_url.replace("gs://", config.STORAGE_BASE_URL, 1)
        response = await get_with_auth_safe_redirects(
            self.http_client,
            download_url,
            headers,
            timeout=DEFAULT_TIMEOUT,
        )
        self._handle_error_response(response)
        return VideoArtifact(data=response.content, mime_type=artifact.mime_type)

    async def _wait_until_file_active(self, url: str) -> str | None:
        """Wait until a Developer File is ready and return its metadata URL."""
        status_url = self._file_status_url(url)
        if status_url is None:
            return None
        headers = self.auth.get_headers()

        try:
            async with asyncio.timeout(config.FILE_POLL_TIMEOUT):
                while True:
                    status_response = await get_with_auth_safe_redirects(
                        self.http_client,
                        status_url,
                        headers,
                        timeout=DEFAULT_TIMEOUT,
                    )
                    self._handle_error_response(status_response)
                    status_data = status_response.json()
                    state = status_data.get("state", "STATE_UNSPECIFIED")
                    if state == "ACTIVE":
                        return status_url
                    if state == "FAILED":
                        error = status_data.get("error", {})
                        detail = error.get("message", "Unknown error")
                        raise ValueError(
                            f"Google Files video processing failed: {detail}"
                        )
                    if state not in ("PROCESSING", "STATE_UNSPECIFIED"):
                        raise ValueError(f"Unexpected Google Files state: {state}")
                    await asyncio.sleep(config.FILE_POLL_INTERVAL)
        except TimeoutError as exc:
            raise TimeoutError(
                f"Google Files video processing timed out after "
                f"{config.FILE_POLL_TIMEOUT} seconds"
            ) from exc

    @staticmethod
    def _file_status_url(url: str) -> str | None:
        """Return the Files metadata URL for a Developer API download URI."""
        parsed = urlsplit(url)
        if (
            parsed.netloc != "generativelanguage.googleapis.com"
            or "/v1beta/files/" not in parsed.path
        ):
            return None
        return urlunsplit(
            (
                parsed.scheme,
                parsed.netloc,
                parsed.path.removesuffix(":download"),
                "",
                "",
            )
        )


__all__ = ["GoogleInteractionsVideosClient"]
