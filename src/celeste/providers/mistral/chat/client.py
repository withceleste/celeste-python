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
            return config.VertexMistralEndpoint.STREAM_CHAT
        return config.VertexMistralEndpoint.CREATE_CHAT

    def _build_url(self, endpoint: str, streaming: bool = False) -> str:
        """Build full URL based on auth type."""
        if isinstance(self.auth, GoogleADC):
            return self.auth.build_url(
                self._get_vertex_endpoint(endpoint, streaming=streaming),
                model_id=self.model.id,
            )
        return f"{config.BASE_URL}{endpoint}"


__all__ = ["MistralChatClient"]
