"""Groq Chat SSE parsing for streaming."""

from typing import Any

from celeste.protocols.chatcompletions import ChatCompletionsStream


class GroqChatStream(ChatCompletionsStream):
    """Mixin for Chat API SSE parsing.

    Inherits shared Chat Completions streaming implementation and captures
    Groq's executed_tools deltas, which arrive on events without content.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        super().__init__(*args, **kwargs)
        self._executed_tools: list[dict[str, Any]] = []

    def _parse_chunk(self, event_data: dict[str, Any]) -> Any:  # noqa: ANN401
        """Capture native executed_tools deltas before delegating."""
        delta = self._get_chunk_delta(event_data)
        executed_tools = delta.get("executed_tools") if delta is not None else None
        if isinstance(executed_tools, list):
            self._executed_tools.extend(
                tool for tool in executed_tools if isinstance(tool, dict)
            )
        return super()._parse_chunk(event_data)


__all__ = ["GroqChatStream"]
