"""Groq Chat SSE parsing for streaming."""

from celeste.protocols.chatcompletions import ChatCompletionsStream


class GroqChatStream(ChatCompletionsStream):
    """Mixin for Chat API SSE parsing.

    Inherits shared Chat Completions streaming implementation.
    No overrides needed — standard Chat Completions SSE format.
    """


__all__ = ["GroqChatStream"]
