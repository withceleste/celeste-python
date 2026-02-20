"""Mistral Chat SSE parsing for streaming."""

from typing import Any

from celeste.io import FinishReason
from celeste.protocols.chatcompletions import ChatCompletionsStream


class MistralChatStream(ChatCompletionsStream):
    """Mixin for Chat API SSE parsing.

    Inherits shared Chat Completions streaming implementation. Overrides:
    - _parse_chunk_content() - No object type check, thinking model list content
    - _parse_chunk_finish_reason() - No object type check
    """

    def _parse_chunk_content(self, event_data: dict[str, Any]) -> str | None:
        """Extract content from SSE event."""
        choices = event_data.get("choices", [])
        if not choices:
            return None

        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            return None

        delta = first_choice.get("delta", {})
        if not isinstance(delta, dict):
            return None

        content_delta = delta.get("content")

        # Handle magistral thinking models that may return list content
        if isinstance(content_delta, list):
            text_parts = []
            for block in content_delta:
                if isinstance(block, dict) and block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
            return "".join(text_parts) if text_parts else None

        return content_delta

    def _parse_chunk_finish_reason(
        self, event_data: dict[str, Any]
    ) -> FinishReason | None:
        """Extract finish reason from SSE event."""
        choices = event_data.get("choices", [])
        if not choices:
            return None

        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            return None

        finish_reason = first_choice.get("finish_reason")
        if finish_reason:
            return FinishReason(reason=finish_reason)

        return None


__all__ = ["MistralChatStream"]
