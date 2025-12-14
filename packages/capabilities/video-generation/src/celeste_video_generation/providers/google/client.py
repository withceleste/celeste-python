"""Google provider client for video generation."""

import asyncio
import base64
import json
import logging
from typing import Any, Unpack

import httpx

from celeste.artifacts import ImageArtifact, VideoArtifact
from celeste.mime_types import ApplicationMimeType, VideoMimeType
from celeste.parameters import ParameterMapper
from celeste_video_generation.client import VideoGenerationClient
from celeste_video_generation.io import (
    VideoGenerationInput,
    VideoGenerationUsage,
)
from celeste_video_generation.parameters import VideoGenerationParameters
from celeste_video_generation.providers.google import config
from celeste_video_generation.providers.google.parameters import (
    GOOGLE_PARAMETER_MAPPERS,
)

logger = logging.getLogger(__name__)


class GoogleVideoGenerationClient(VideoGenerationClient):
    """Google client for video generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return GOOGLE_PARAMETER_MAPPERS

    def _validate_artifacts(
        self,
        inputs: VideoGenerationInput,
        **parameters: Unpack[VideoGenerationParameters],
    ) -> tuple[VideoGenerationInput, dict[str, Any]]:
        """Validate and prepare artifacts for Google Veo API."""

        def convert_to_base64_uri(img: ImageArtifact) -> ImageArtifact:
            if img.data:
                file_data = img.data
            elif img.path:
                with open(img.path, "rb") as f:
                    file_data = f.read()
            else:
                msg = "ImageArtifact must have data or path"
                raise ValueError(msg)

            base64_data = base64.b64encode(file_data).decode("utf-8")
            mime_type = img.mime_type.value if img.mime_type else "image/jpeg"

            return ImageArtifact(
                url=f"data:image/{mime_type.split('/')[-1]};base64,{base64_data}",
                mime_type=img.mime_type,
                metadata=img.metadata,
            )

        reference_images = parameters.get("reference_images")
        if reference_images:
            converted_images = [convert_to_base64_uri(img) for img in reference_images]
            parameters["reference_images"] = converted_images

        first_frame = parameters.get("first_frame")
        if first_frame:
            parameters["first_frame"] = convert_to_base64_uri(first_frame)

        last_frame = parameters.get("last_frame")
        if last_frame:
            parameters["last_frame"] = convert_to_base64_uri(last_frame)

        return inputs, dict(parameters)

    def _init_request(self, inputs: VideoGenerationInput) -> dict[str, Any]:
        """Initialize request from Google API format."""
        instance: dict[str, Any] = {"prompt": inputs.prompt}

        request: dict[str, Any] = {"instances": [instance]}
        request["parameters"] = {}

        return request

    def _parse_usage(self, response_data: dict[str, Any]) -> VideoGenerationUsage:
        """Parse usage from response."""
        return VideoGenerationUsage()

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[VideoGenerationParameters],
    ) -> VideoArtifact:
        """Parse content from response."""
        try:
            generate_response = response_data.get("response", {}).get(
                "generateVideoResponse", {}
            )
            generated_samples = generate_response.get("generatedSamples", [])
            if not generated_samples:
                msg = "No generated samples in response"
                raise ValueError(msg)

            video_data = generated_samples[0].get("video", {})
            uri = video_data.get("uri")
            if not uri:
                msg = "No video URI in response"
                raise ValueError(msg)

            video_artifact = VideoArtifact(url=uri)

            transformed = self._transform_output(video_artifact, **parameters)
            if isinstance(transformed, VideoArtifact):
                return transformed
            return video_artifact
        except (KeyError, IndexError) as e:
            msg = f"Invalid response structure: {e}"
            raise ValueError(msg) from e

    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[VideoGenerationParameters],
    ) -> httpx.Response:
        """Make HTTP request with async polling for Google video generation."""
        model_id = self.model.id
        endpoint = config.GENERATE_ENDPOINT.format(model_id=model_id)
        url = f"{config.BASE_URL}{endpoint}"

        headers = {
            "x-goog-api-key": self.api_key.get_secret_value(),
            "Content-Type": ApplicationMimeType.JSON,
        }

        logger.info(f"Initiating video generation with model {model_id}")
        response = await self.http_client.post(
            url,
            headers=headers,
            json_body=request_body,
            timeout=config.DEFAULT_TIMEOUT,
        )

        self._handle_error_response(response)
        operation_data = response.json()

        operation_name = operation_data["name"]
        logger.info(f"Video generation started: {operation_name}")

        poll_url = f"{config.BASE_URL}{config.POLL_ENDPOINT.format(operation_name=operation_name)}"
        poll_headers = {"x-goog-api-key": self.api_key.get_secret_value()}

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

        return httpx.Response(
            200,
            content=json.dumps(operation_data).encode(),
            headers={"Content-Type": ApplicationMimeType.JSON},
        )

    async def download_content(self, artifact: VideoArtifact) -> VideoArtifact:
        """Download video content from URI.

        Google-specific method. Google Veo returns gs:// URIs that require
        downloading with API key authentication. Other providers return video
        content directly in the response.
        """
        if not artifact.url:
            msg = "VideoArtifact has no URL to download from"
            raise ValueError(msg)

        download_url = artifact.url
        if download_url.startswith("gs://"):
            download_url = download_url.replace("gs://", config.STORAGE_BASE_URL, 1)

        logger.info(f"Downloading video from: {download_url}")

        headers = {"x-goog-api-key": self.api_key.get_secret_value()}

        response = await self.http_client.get(
            download_url,
            headers=headers,
            timeout=config.DEFAULT_TIMEOUT,
            follow_redirects=True,
        )

        self._handle_error_response(response)
        video_data = response.content

        return VideoArtifact(
            url=artifact.url,  # Keep original URI
            data=video_data,
            mime_type=VideoMimeType.MP4,  # Default to MP4 for videos
            metadata=artifact.metadata,
        )
