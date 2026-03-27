"""Chat Completions protocol SSE parsing for streaming."""

import contextlib
import json
from typing import Any

from celeste.io import FinishReason
from celeste.tools import ToolCall

from .client import ChatCompletionsClient


class ChatCompletionsStream:
    """Chat Completions protocol SSE parsing mixin.

    Provides shared implementation for streaming parsing (protocol level):
    - _parse_chunk_content(event_data) - Extract content from SSE event
    - _parse_chunk_usage(event_data) - Extract and normalize usage from SSE event
    - _parse_chunk_finish_reason(event_data) - Extract finish reason from SSE event
    - _parse_chunk(event_data) - Capture tool_call deltas before delegating
    - _aggregate_tool_calls(chunks, raw_events) - Reconstruct tool calls from deltas
    - _build_stream_metadata(raw_events) - Filter content-only events

    Provider streams inherit this and override methods for provider-specific behavior
    (e.g., thinking model content parsing, non-standard usage locations).

    Modality streams call super() methods which resolve to this via MRO.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        super().__init__(*args, **kwargs)
        self._tool_call_deltas: dict[int, dict[str, Any]] = {}

    def _parse_chunk_content(self, event_data: dict[str, Any]) -> str | None:
        """Extract content from SSE event."""
        object_type = event_data.get("object")
        if object_type != "chat.completion.chunk":
            return None

        choices = event_data.get("choices", [])
        if not choices:
            return None

        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            return None

        delta = first_choice.get("delta", {})
        if not isinstance(delta, dict):
            return None

        return delta.get("content") or None

    def _parse_chunk_usage(
        self, event_data: dict[str, Any]
    ) -> dict[str, int | float | None] | None:
        """Extract and normalize usage from SSE event."""
        usage_data = event_data.get("usage")
        if isinstance(usage_data, dict):
            return ChatCompletionsClient.map_usage_fields(usage_data)

        return None

    def _parse_chunk_finish_reason(
        self, event_data: dict[str, Any]
    ) -> FinishReason | None:
        """Extract finish reason from SSE event."""
        object_type = event_data.get("object")
        if object_type != "chat.completion.chunk":
            return None

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

    def _parse_chunk(self, event_data: dict[str, Any]) -> Any:  # noqa: ANN401
        """Capture tool_call deltas before delegating to base _parse_chunk."""
        choices = event_data.get("choices", [])
        if choices and isinstance(choices[0], dict):
            delta = choices[0].get("delta", {})
            if isinstance(delta, dict):
                for tc_delta in delta.get("tool_calls") or []:
                    idx = tc_delta.get("index", 0)
                    if idx not in self._tool_call_deltas:
                        self._tool_call_deltas[idx] = {
                            "id": tc_delta.get("id", ""),
                            "name": tc_delta.get("function", {}).get("name", ""),
                            "arguments": "",
                        }
                    else:
                        if tc_delta.get("id"):
                            self._tool_call_deltas[idx]["id"] = tc_delta["id"]
                        fn = tc_delta.get("function", {})
                        if fn.get("name"):
                            self._tool_call_deltas[idx]["name"] = fn["name"]
                    # Accumulate argument fragments
                    fn = tc_delta.get("function", {})
                    self._tool_call_deltas[idx]["arguments"] += fn.get("arguments", "")
        return super()._parse_chunk(event_data)  # type: ignore[misc]

    def _aggregate_tool_calls(
        self, chunks: list, raw_events: list[dict[str, Any]]
    ) -> list[ToolCall]:
        """Reconstruct tool calls from accumulated Chat Completions deltas."""
        result: list[ToolCall] = []
        for tc in self._tool_call_deltas.values():
            arguments: dict[str, Any] = {}
            if tc["arguments"]:
                with contextlib.suppress(json.JSONDecodeError, ValueError, TypeError):
                    arguments = json.loads(tc["arguments"])
            result.append(ToolCall(id=tc["id"], name=tc["name"], arguments=arguments))
        return result

    def _build_stream_metadata(
        self, raw_events: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Filter content-only events for size efficiency."""
        filtered = [event for event in raw_events if event.get("usage")]
        return super()._build_stream_metadata(filtered)  # type: ignore[misc, no-any-return]


__all__ = ["ChatCompletionsStream"]
