"""DeepSeek Chat SSE parsing for streaming."""

from typing import Any

from celeste.protocols.chatcompletions import ChatCompletionsStream

from .client import DeepSeekChatClient


class DeepSeekChatStream(ChatCompletionsStream):
    """Mixin for Chat API SSE parsing.

    Inherits shared Chat Completions streaming implementation. Overrides:
    - _parse_chunk_usage() - Uses DeepSeek's extended usage fields
    """

    def _parse_chunk_usage(
        self, event_data: dict[str, Any]
    ) -> dict[str, int | float | None] | None:
        """Extract and normalize usage from SSE event."""
        usage_data = event_data.get("usage")
        if isinstance(usage_data, dict):
            return DeepSeekChatClient.map_usage_fields(usage_data)

        return None


__all__ = ["DeepSeekChatStream"]
