"""Mistral Chat SSE parsing for streaming."""

from typing import Any

from celeste.io import FinishReason
from celeste.protocols.chatcompletions import ChatCompletionsStream


def _extract_thinking_text(content_blocks: list[Any]) -> list[str]:
    """Extract thinking text from Mistral Magistral list content."""
    parts: list[str] = []
    for block in content_blocks:
        if isinstance(block, dict) and block.get("type") == "thinking":
            for part in block.get("thinking", []):
                if isinstance(part, dict) and part.get("type") == "text":
                    text = part.get("text", "")
                    if text:
                        parts.append(text)
    return parts


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

        return content_delta or None

    def _parse_chunk_reasoning(self, event_data: dict[str, Any]) -> str | None:
        """Extract thinking content from Mistral SSE event."""
        choices = event_data.get("choices", [])
        if not choices or not isinstance(choices[0], dict):
            return None

        delta = choices[0].get("delta", {})
        if not isinstance(delta, dict):
            return None

        content_delta = delta.get("content")
        if not isinstance(content_delta, list):
            return None

        parts = _extract_thinking_text(content_delta)
        return "".join(parts) if parts else None

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
