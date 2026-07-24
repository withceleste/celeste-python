"""Topaz Labs Image API client mixin."""

import asyncio
import time
from collections.abc import AsyncIterator
from typing import Any, ClassVar

from celeste.client import APIMixin
from celeste.exceptions import StreamingNotSupportedError
from celeste.io import FinishReason
from celeste.mime_types import ApplicationMimeType
from celeste.utils import detect_mime_type

from . import config


def form_field_value(value: object) -> str:
    """Encode a form field for Topaz multipart requests."""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


class TopazLabsImageClient(APIMixin):
    """Mixin for Topaz Labs Image API intents.

    Async polling workflow:
    1. POST multipart to the model-specific intent endpoint
    2. Poll GET /status/{process_id} until Completed/Failed/Cancelled
    3. GET /download/{process_id} for the presigned download URL

    Submit path is always resolved from the model id map in config, not from
    the modality ClassVar (which is only a capability sentinel).
    """

    _content_fields: ClassVar[set[str]] = {"download_url", "url"}

    def _build_request(
        self,
        inputs: Any,
        extra_body: dict[str, Any] | None = None,
        streaming: bool = False,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Build request with model ID."""
        request_body = super()._build_request(
            inputs, extra_body=extra_body, streaming=streaming, **parameters
        )
        request_body["model"] = self.model.id
        return request_body

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Submit image job, poll status, then fetch download URL."""
        submit_endpoint = config.submit_endpoint_for_model(self.model.id)
        submit_data = await self._submit_job(
            request_body, submit_endpoint, extra_headers=extra_headers
        )
        process_id = submit_data.get("process_id")
        if not process_id:
            msg = f"No process_id in {self.provider} response"
            raise ValueError(msg)

        status_data = await self._poll_status(process_id, extra_headers=extra_headers)
        download_data = await self._fetch_download(
            process_id, extra_headers=extra_headers
        )
        return {
            **download_data,
            "_status": status_data,
            "_submit_metadata": submit_data,
        }

    async def _submit_job(
        self,
        request_body: dict[str, Any],
        endpoint: str,
        *,
        extra_headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """POST multipart image job and return submit JSON."""
        image_artifact = request_body.pop("image")
        image_bytes = image_artifact.get_bytes()
        mime = image_artifact.mime_type or detect_mime_type(image_bytes)
        mime_str = mime.value if mime else "application/octet-stream"

        files = {"image": ("image", image_bytes, mime_str)}
        model = request_body.pop("model")
        data: dict[str, str] = {"model": model}
        for key, value in request_body.items():
            if value is not None:
                data[key] = form_field_value(value)

        response = await self.http_client.post_multipart(
            f"{config.BASE_URL}{endpoint}",
            headers=self._merge_headers(self.auth.get_headers(), extra_headers),
            files=files,
            data=data,
        )
        self._handle_error_response(response)
        submit_data: dict[str, Any] = response.json()
        return submit_data

    async def _poll_status(
        self,
        process_id: str,
        *,
        extra_headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Poll status until Completed or terminal failure."""
        headers = self._merge_headers(
            {**self.auth.get_headers(), "Accept": ApplicationMimeType.JSON},
            extra_headers,
        )
        status_url = (
            f"{config.BASE_URL}"
            f"{config.TopazLabsImageEndpoint.STATUS.format(process_id=process_id)}"
        )
        start_time = time.monotonic()

        while True:
            elapsed = time.monotonic() - start_time
            if elapsed >= config.POLLING_TIMEOUT:
                msg = (
                    f"{self.provider} polling timed out after "
                    f"{config.POLLING_TIMEOUT} seconds"
                )
                raise TimeoutError(msg)

            poll_response = await self.http_client.get(status_url, headers=headers)
            self._handle_error_response(poll_response)
            poll_data: dict[str, Any] = poll_response.json()
            status = poll_data.get("status")

            if status == "Completed":
                return poll_data
            if status in ("Failed", "Cancelled"):
                error_msg = poll_data.get("error") or poll_data.get("message") or status
                msg = f"{self.provider} image upscale failed: {error_msg}"
                raise ValueError(msg)

            await asyncio.sleep(config.POLLING_INTERVAL)

    async def _fetch_download(
        self,
        process_id: str,
        *,
        extra_headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Fetch presigned download URL for a completed process."""
        headers = self._merge_headers(
            {**self.auth.get_headers(), "Accept": ApplicationMimeType.JSON},
            extra_headers,
        )
        download_url = (
            f"{config.BASE_URL}"
            f"{config.TopazLabsImageEndpoint.DOWNLOAD.format(process_id=process_id)}"
        )
        response = await self.http_client.get(download_url, headers=headers)
        self._handle_error_response(response)
        download_data: dict[str, Any] = response.json()
        return download_data

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """Topaz Labs Image API does not support SSE streaming in this client."""
        raise StreamingNotSupportedError(model_id=self.model.id)

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """Topaz Image responses do not expose usage fields in this client."""
        return {}

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Parse download URL from response."""
        download_url = response_data.get("download_url") or response_data.get("url")
        if not download_url:
            msg = "No download URL in response"
            raise ValueError(msg)
        return download_url

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """Map completed Topaz status to finish reason when present."""
        status = response_data.get("_status", {}).get("status")
        if status == "Completed":
            return FinishReason(reason="COMPLETE")
        return FinishReason(reason=None)


__all__ = ["TopazLabsImageClient", "form_field_value"]
