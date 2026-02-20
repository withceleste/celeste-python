"""XAI Responses SSE parsing for streaming."""

from celeste.protocols.openresponses.streaming import OpenResponsesStream


class XAIResponsesStream(OpenResponsesStream):
    """XAI Responses SSE parsing."""


__all__ = ["XAIResponsesStream"]
