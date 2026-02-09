"""Google Embeddings API client mixin."""

from collections.abc import AsyncIterator
from typing import Any

from celeste.client import APIMixin
from celeste.exceptions import StreamingNotSupportedError
from celeste.io import FinishReason
from celeste.mime_types import ApplicationMimeType

from ..auth import GoogleADC
from . import config


class GoogleEmbeddingsClient(APIMixin):
    """Mixin for Embeddings API capabilities.

    Provides shared implementation for embeddings using the Embeddings API:
    - _make_request() - HTTP POST to embedContent or batchEmbedContents endpoint
    - _parse_content() - Extract embedding vectors (generic)

    Auth-based endpoint selection:
    - GoogleADC auth -> Vertex AI endpoints
    - API key auth -> Gemini API endpoints

    Capability clients extend via super():
        class GoogleEmbeddingsClient(GoogleEmbeddingsClient, EmbeddingsClient):
            def _parse_content(self, response_data, **params):
                return super()._parse_content(response_data)  # No transformation needed
    """

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        **parameters: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """Embeddings API does not support SSE streaming in this client."""
        raise StreamingNotSupportedError(model_id=self.model.id)

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | float | None]:
        """Map Google Embeddings usage fields to unified names.

        Embeddings API doesn't provide usage metadata.
        """
        return {}

    def _get_vertex_endpoint(self, gemini_endpoint: str) -> str:
        """Map Gemini Embeddings endpoint to Vertex AI endpoint."""
        mapping: dict[str, str] = {
            config.GoogleEmbeddingsEndpoint.EMBED_CONTENT: config.VertexEmbeddingsEndpoint.EMBED_CONTENT,
            config.GoogleEmbeddingsEndpoint.BATCH_EMBED_CONTENTS: config.VertexEmbeddingsEndpoint.BATCH_EMBED_CONTENTS,
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

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Make HTTP request to embeddings endpoint."""
        # Vertex :predict expects {"instances": [{"content": "..."}]} format
        if isinstance(self.auth, GoogleADC):
            if "requests" in request_body:
                texts = [
                    req["content"]["parts"][0]["text"]
                    for req in request_body["requests"]
                ]
            else:
                texts = [request_body["content"]["parts"][0]["text"]]
            request_body = {"instances": [{"content": text} for text in texts]}

        is_batch = "requests" in request_body
        endpoint_template = (
            config.GoogleEmbeddingsEndpoint.BATCH_EMBED_CONTENTS
            if is_batch
            else config.GoogleEmbeddingsEndpoint.EMBED_CONTENT
        )
        if endpoint is None:
            endpoint = endpoint_template

        headers = {
            **self.auth.get_headers(),
            "Content-Type": ApplicationMimeType.JSON,
        }

        response = await self.http_client.post(
            self._build_url(endpoint),
            headers=headers,
            json_body=request_body,
        )
        self._handle_error_response(response)
        data: dict[str, Any] = response.json()
        return data

    def _parse_content(self, response_data: dict[str, Any]) -> list[list[float]]:
        """Extract embedding vectors from response.

        Returns list of embedding vectors (already generic - no artifacts needed).
        Handles both Gemini API and Vertex AI :predict response formats.
        """
        # Vertex :predict response
        if "predictions" in response_data:
            return [
                pred["embeddings"]["values"] for pred in response_data["predictions"]
            ]

        # Gemini single embedding response
        if "embedding" in response_data:
            return [response_data["embedding"]["values"]]

        # Gemini batch embedding response
        if "embeddings" in response_data:
            return [emb["values"] for emb in response_data["embeddings"]]

        msg = "Unexpected response format: missing 'embedding', 'embeddings', or 'predictions' field"
        raise ValueError(msg)

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """Embeddings API doesn't provide usage metadata."""
        return GoogleEmbeddingsClient.map_usage_fields(response_data)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """Embeddings API doesn't provide finish reasons."""
        return FinishReason(reason=None)

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata, filtering out embedding content."""
        content_fields = {"embedding", "embeddings"}
        filtered_data = {
            k: v for k, v in response_data.items() if k not in content_fields
        }
        return super()._build_metadata(filtered_data)


__all__ = ["GoogleEmbeddingsClient"]
