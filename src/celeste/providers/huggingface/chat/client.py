"""HuggingFace Chat API client mixin."""

from typing import ClassVar

from celeste.protocols.chatcompletions import ChatCompletionsClient

from . import config


class HuggingFaceChatClient(ChatCompletionsClient):
    """Mixin for HuggingFace Chat API capabilities.

    Inherits shared Chat Completions implementation. Only overrides:
    - _default_base_url - HuggingFace router base URL
    - _default_endpoint - HuggingFace uses /v1/chat/completions
    """

    _default_base_url: ClassVar[str] = config.BASE_URL
    _default_endpoint: ClassVar[str] = (
        config.HuggingFaceChatEndpoint.CREATE_CHAT_COMPLETION
    )


__all__ = ["HuggingFaceChatClient"]
