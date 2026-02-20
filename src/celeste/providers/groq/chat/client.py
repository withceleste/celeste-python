"""Groq Chat API client mixin."""

from typing import ClassVar

from celeste.protocols.chatcompletions import ChatCompletionsClient

from . import config


class GroqChatClient(ChatCompletionsClient):
    """Mixin for Groq Chat API capabilities.

    Inherits shared Chat Completions implementation. Only overrides:
    - _default_base_url - Groq API base URL
    - _default_endpoint - Groq uses /openai/v1/chat/completions
    """

    _default_base_url: ClassVar[str] = config.BASE_URL
    _default_endpoint: ClassVar[str] = config.GroqChatEndpoint.CREATE_CHAT_COMPLETION


__all__ = ["GroqChatClient"]
