"""Moonshot Chat SSE parsing for streaming."""

from typing import Any

from celeste.protocols.chatcompletions import ChatCompletionsStream

from .client import MoonshotChatClient


class MoonshotChatStream(ChatCompletionsStream):
    """Mixin for Chat API SSE parsing.

    Inherits shared Chat Completions streaming implementation. Overrides:
    - _parse_chunk_usage() - Checks both top-level and choices[0] usage locations
    """

    def _parse_chunk_usage(
        self, event_data: dict[str, Any]
    ) -> dict[str, int | float | None] | None:
        """Extract and normalize usage from SSE event."""
        # Check both top-level and choices[0] (Moonshot's non-standard location)
        usage_data = event_data.get("usage")
        if not isinstance(usage_data, dict):
            choices = event_data.get("choices", [])
            if choices and isinstance(choices[0], dict):
                usage_data = choices[0].get("usage")

        if isinstance(usage_data, dict):
            return MoonshotChatClient.map_usage_fields(usage_data)

        return None


__all__ = ["MoonshotChatStream"]
