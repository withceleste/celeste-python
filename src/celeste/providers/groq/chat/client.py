"""Groq Chat API client mixin."""

from typing import Any, ClassVar

from celeste.protocols.chatcompletions import ChatCompletionsClient

from . import config


class GroqChatClient(ChatCompletionsClient):
    """Mixin for Groq Chat API capabilities.

    Inherits shared Chat Completions implementation. Only overrides:
    - _default_base_url - Groq API base URL
    - _default_endpoint - Groq uses /openai/v1/chat/completions
    - _build_request() - Requests usage in streaming responses
    """

    _default_base_url: ClassVar[str] = config.BASE_URL
    _default_endpoint: ClassVar[str] = config.GroqChatEndpoint.CREATE_CHAT_COMPLETION

    def _build_request(
        self,
        inputs: Any,
        extra_body: dict[str, Any] | None = None,
        streaming: bool = False,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Request the terminal usage chunk required for streamed billing."""
        request_body = super()._build_request(
            inputs, extra_body=extra_body, streaming=streaming, **parameters
        )
        if streaming:
            request_body["stream_options"] = {"include_usage": True}
        return request_body


__all__ = ["GroqChatClient"]
