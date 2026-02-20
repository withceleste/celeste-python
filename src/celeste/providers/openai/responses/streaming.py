"""OpenAI Responses SSE parsing for streaming."""

from celeste.protocols.openresponses.streaming import OpenResponsesStream


class OpenAIResponsesStream(OpenResponsesStream):
    """OpenAI Responses SSE parsing."""


__all__ = ["OpenAIResponsesStream"]
