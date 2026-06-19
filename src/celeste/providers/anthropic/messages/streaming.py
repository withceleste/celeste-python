"""Anthropic Messages SSE parsing for streaming."""

import contextlib
import json
from typing import Any

from celeste.io import FinishReason
from celeste.types import ToolActivity, ToolActivityStatus

from .client import AnthropicMessagesClient


class AnthropicMessagesStream:
    """Mixin for Messages API SSE parsing.

    Provides shared implementation for streaming parsing (provider API level):
    - _parse_chunk_content(event_data) - Extract content from SSE event
    - _parse_chunk_usage(event_data) - Extract and normalize usage from SSE event
    - _parse_chunk_finish_reason(event_data) - Extract finish reason from SSE event

    Modality streams call super() methods which resolve to this via MRO.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        super().__init__(*args, **kwargs)
        self._content_blocks: dict[int, dict[str, Any]] = {}

    def _parse_chunk(self, event_data: dict[str, Any]) -> Any:  # noqa: ANN401
        """Capture native content blocks before delegating to the modality stream."""
        event_type = event_data.get("type")
        if event_type == "content_block_start":
            block = event_data.get("content_block", {})
            block_type = block.get("type")
            idx = event_data.get("index", len(self._content_blocks))
            if block_type == "server_tool_use":
                self._content_blocks[idx] = {
                    "type": "server_tool_use",
                    "id": block.get("id", ""),
                    "name": block.get("name", ""),
                    "input_json": "",
                }
            elif block_type == "web_search_tool_result":
                self._content_blocks[idx] = block
            elif block_type == "text":
                self._content_blocks[idx] = {
                    "type": "text",
                    "text": block.get("text", ""),
                    "citations": [],
                }
        elif event_type == "content_block_delta":
            delta = event_data.get("delta", {})
            delta_type = delta.get("type")
            idx = event_data.get("index", -1)
            block = self._content_blocks.get(idx)
            if delta_type == "input_json_delta":
                if block and block.get("type") == "server_tool_use":
                    block["input_json"] += delta.get("partial_json", "")
            elif delta_type in {"text_delta", "citations_delta"}:
                block = self._content_blocks.setdefault(
                    idx, {"type": "text", "text": "", "citations": []}
                )
                if delta_type == "text_delta":
                    block["text"] += delta.get("text", "")
                else:
                    citation = delta.get("citation")
                    if isinstance(citation, dict):
                        block["citations"].append(citation)
        return super()._parse_chunk(event_data)  # type: ignore[misc]

    def _aggregate_content_blocks(self) -> list[dict[str, Any]]:
        """Return reconstructed native Anthropic content blocks."""
        blocks: list[dict[str, Any]] = []
        for idx in sorted(self._content_blocks):
            block = self._content_blocks[idx]
            if block.get("type") == "server_tool_use":
                input_data: dict[str, Any] = {}
                if block["input_json"]:
                    with contextlib.suppress(ValueError, TypeError):
                        input_data = json.loads(block["input_json"])
                blocks.append(
                    {
                        "type": "server_tool_use",
                        "id": block["id"],
                        "name": block["name"],
                        "input": input_data,
                    }
                )
            else:
                blocks.append(block)
        return blocks

    def _parse_chunk_content(self, event_data: dict[str, Any]) -> str | None:
        """Extract content from SSE event.

        Returns content string if present, None otherwise.
        """
        event_type = event_data.get("type")

        if event_type == "content_block_delta":
            delta = event_data.get("delta", {})
            if delta.get("type") == "text_delta":
                return delta.get("text") or None

        return None

    def _parse_chunk_reasoning(self, event_data: dict[str, Any]) -> str | None:
        """Extract thinking content from SSE event."""
        if event_data.get("type") == "content_block_delta":
            delta = event_data.get("delta", {})
            if delta.get("type") == "thinking_delta":
                return delta.get("thinking") or None
        return None

    def _parse_chunk_tool_activity(
        self, event_data: dict[str, Any]
    ) -> ToolActivity | None:
        """Extract native web-search activity from content block starts."""
        if event_data.get("type") != "content_block_start":
            return None
        block = event_data.get("content_block", {})
        block_type = block.get("type")
        if block_type == "server_tool_use" and block.get("name") == "web_search":
            return ToolActivity(
                tool_name="web_search", status=ToolActivityStatus.STARTED
            )
        if block_type == "web_search_tool_result":
            return ToolActivity(
                tool_name="web_search", status=ToolActivityStatus.COMPLETED
            )
        return None

    def _parse_chunk_usage(
        self, event_data: dict[str, Any]
    ) -> dict[str, int | float | None] | None:
        """Extract and normalize usage from SSE event.

        Returns normalized usage dict if present, None otherwise.
        """
        event_type = event_data.get("type")

        if event_type in ("message_delta", "message_stop"):
            usage_data = event_data.get("usage")
            if usage_data:
                return AnthropicMessagesClient.map_usage_fields(usage_data)

        return None

    def _parse_chunk_finish_reason(
        self, event_data: dict[str, Any]
    ) -> FinishReason | None:
        """Extract finish reason from SSE event.

        Returns FinishReason if present, None otherwise.
        """
        event_type = event_data.get("type")

        if event_type == "message_delta":
            delta = event_data.get("delta", {})
            stop_reason = delta.get("stop_reason")
            if stop_reason:
                return FinishReason(reason=stop_reason)

        return None

    def _build_stream_metadata(
        self, raw_events: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Filter content-only events for size efficiency (content is in Output.content)."""
        filtered = [e for e in raw_events if e.get("type") != "content_block_delta"]
        return super()._build_stream_metadata(filtered)  # type: ignore[misc]


__all__ = ["AnthropicMessagesStream"]
