"""BFL (Black Forest Labs) client implementation for FLUX.2 image generation."""

import asyncio
import json
import time
from typing import Any, Unpack

import httpx

from celeste.artifacts import ImageArtifact
from celeste.mime_types import ApplicationMimeType
from celeste.parameters import ParameterMapper
from celeste_image_generation.client import ImageGenerationClient
from celeste_image_generation.io import (
    ImageGenerationFinishReason,
    ImageGenerationInput,
    ImageGenerationUsage,
)
from celeste_image_generation.parameters import ImageGenerationParameters

from . import config
from .parameters import BFL_PARAMETER_MAPPERS


class BFLImageGenerationClient(ImageGenerationClient):
    """Black Forest Labs client for image generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return BFL_PARAMETER_MAPPERS

    def _init_request(self, inputs: ImageGenerationInput) -> dict[str, Any]:
        """Initialize request for BFL API format."""
        return {
            "prompt": inputs.prompt,
        }

    def _parse_usage(self, response_data: dict[str, Any]) -> ImageGenerationUsage:
        """Parse usage from response."""
        submit_metadata = response_data.get("_submit_metadata", {})
        cost = submit_metadata.get("cost")

        return ImageGenerationUsage(
            billed_units=float(cost) if cost is not None else None,
        )

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[ImageGenerationParameters],
    ) -> ImageArtifact:
        """Parse content from response."""
        result = response_data.get("result", {})
        sample_url = result.get("sample")

        if not sample_url:
            msg = f"No image URL in {self.provider} response"
            raise ValueError(msg)

        return ImageArtifact(url=sample_url)

    def _parse_finish_reason(
        self, response_data: dict[str, Any]
    ) -> ImageGenerationFinishReason | None:
        """Parse finish reason from response."""
        status = response_data.get("status")
        if status == "Ready":
            return ImageGenerationFinishReason(reason="COMPLETE")
        elif status in ("Error", "Failed"):
            error_msg = response_data.get("error", "Generation failed")
            return ImageGenerationFinishReason(reason="ERROR", message=error_msg)
        return None

    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[ImageGenerationParameters],
    ) -> httpx.Response:
        """Make HTTP request(s) and return response object."""
        headers = {
            config.AUTH_HEADER_NAME: self.api_key.get_secret_value(),
            "Content-Type": ApplicationMimeType.JSON,
            "Accept": ApplicationMimeType.JSON,
        }

        endpoint = config.ENDPOINT.format(model_id=self.model.id)

        submit_response = await self.http_client.post(
            f"{config.BASE_URL}{endpoint}",
            headers=headers,
            json_body=request_body,
        )

        if submit_response.status_code != 200:
            return submit_response

        submit_data = submit_response.json()
        polling_url = submit_data.get("polling_url")

        if not polling_url:
            msg = f"No polling_url in {self.provider} response"
            raise ValueError(msg)

        start_time = time.monotonic()
        poll_headers = {
            config.AUTH_HEADER_NAME: self.api_key.get_secret_value(),
            "Accept": ApplicationMimeType.JSON,
        }

        while True:
            elapsed = time.monotonic() - start_time
            if elapsed >= config.POLLING_TIMEOUT:
                msg = f"{self.provider} polling timed out after {config.POLLING_TIMEOUT} seconds"
                raise TimeoutError(msg)

            poll_response = await self.http_client.get(
                polling_url,
                headers=poll_headers,
            )

            if poll_response.status_code != 200:
                return poll_response

            poll_data = poll_response.json()
            status = poll_data.get("status")

            if status == "Ready":
                final_data = {
                    **poll_data,
                    "_submit_metadata": submit_data,
                }
                return httpx.Response(
                    status_code=200,
                    content=json.dumps(final_data).encode("utf-8"),
                    headers={"content-type": "application/json"},
                    request=httpx.Request("GET", polling_url),
                )
            elif status in ("Error", "Failed"):
                return httpx.Response(
                    status_code=400,
                    content=json.dumps(poll_data).encode("utf-8"),
                    headers={"content-type": "application/json"},
                    request=httpx.Request("GET", polling_url),
                )

            await asyncio.sleep(config.POLLING_INTERVAL)


__all__ = ["BFLImageGenerationClient"]
