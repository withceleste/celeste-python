"""Mistral Chat API client mixin."""

from typing import ClassVar

from celeste.protocols.chatcompletions import ChatCompletionsClient
from celeste.providers.google.auth import GoogleADC

from . import config


class MistralChatClient(ChatCompletionsClient):
    """Mixin for Mistral Chat API capabilities.

    Inherits shared Chat Completions implementation. Overrides:
    - _build_url() - Vertex AI endpoint routing with streaming awareness
    """

    _default_base_url: ClassVar[str] = config.BASE_URL

    def _get_vertex_endpoint(
        self, mistral_endpoint: str, streaming: bool = False
    ) -> str:
        """Map Mistral endpoint to Vertex AI endpoint."""
        if streaming:
            return config.VertexChatEndpoint.STREAM_CHAT
        return config.VertexChatEndpoint.CREATE_CHAT

    def _build_url(self, endpoint: str, streaming: bool = False) -> str:
        """Build the request URL, honoring an explicit base_url override."""
        if isinstance(self.auth, GoogleADC):
            vertex_url = self.auth.build_url(
                self._get_vertex_endpoint(endpoint, streaming=streaming),
                model_id=self.model.id,
            )
            if self.base_url is None:
                return vertex_url
            vertex_path = vertex_url.removeprefix(self.auth.get_vertex_base_url())
            return f"{self.base_url.rstrip('/')}{vertex_path}"
        return super()._build_url(endpoint, streaming)


__all__ = ["MistralChatClient"]
