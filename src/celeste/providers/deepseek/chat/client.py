"""DeepSeek Chat API client mixin."""

from typing import Any, ClassVar

from celeste.core import UsageField
from celeste.protocols.chatcompletions import ChatCompletionsClient
from celeste.providers.google.auth import GoogleADC

from . import config


class DeepSeekChatClient(ChatCompletionsClient):
    """Mixin for DeepSeek Chat API capabilities.

    Inherits shared Chat Completions implementation. Overrides:
    - _build_url() - Vertex AI endpoint routing
    - map_usage_fields() - Extended usage fields (cached_tokens, reasoning_tokens)
    """

    _default_base_url: ClassVar[str] = config.BASE_URL

    def _get_vertex_endpoint(self, deepseek_endpoint: str) -> str:
        """Map DeepSeek endpoint to Vertex AI endpoint."""
        mapping: dict[str, str] = {
            config.DeepSeekChatEndpoint.CREATE_CHAT: config.VertexDeepSeekEndpoint.CREATE_CHAT,
        }
        vertex_endpoint = mapping.get(deepseek_endpoint)
        if vertex_endpoint is None:
            raise ValueError(f"No Vertex AI endpoint mapping for: {deepseek_endpoint}")
        return vertex_endpoint

    def _build_url(self, endpoint: str, streaming: bool = False) -> str:
        """Build full URL based on auth type."""
        if isinstance(self.auth, GoogleADC):
            return self.auth.build_url(self._get_vertex_endpoint(endpoint))
        return f"{config.BASE_URL}{endpoint}"

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | float | None]:
        """Map DeepSeek usage fields to unified names.

        Shared by client and streaming across all capabilities.
        """
        prompt_tokens_details = usage_data.get("prompt_tokens_details") or {}
        completion_tokens_details = usage_data.get("completion_tokens_details") or {}
        return {
            UsageField.INPUT_TOKENS: usage_data.get("prompt_tokens"),
            UsageField.OUTPUT_TOKENS: usage_data.get("completion_tokens"),
            UsageField.TOTAL_TOKENS: usage_data.get("total_tokens"),
            UsageField.CACHED_TOKENS: prompt_tokens_details.get("cached_tokens"),
            UsageField.REASONING_TOKENS: completion_tokens_details.get(
                "reasoning_tokens"
            ),
        }


__all__ = ["DeepSeekChatClient"]
