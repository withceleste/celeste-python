"""XAI Responses SSE parsing for streaming."""

from typing import Any

from celeste.protocols.openresponses.streaming import OpenResponsesStream
from celeste.types import ToolActivity, ToolActivityStatus


class XAIResponsesStream(OpenResponsesStream):
    """XAI Responses SSE parsing."""

    def _parse_chunk_tool_activity(
        self, event_data: dict[str, Any]
    ) -> ToolActivity | None:
        """Extract xAI native image-generation activity."""
        event_type = event_data.get("type")
        if event_type == "response.image_generation_call.in_progress":
            return ToolActivity(
                tool_name="generate_image", status=ToolActivityStatus.STARTED
            )
        if event_type == "response.image_generation_call.completed":
            return ToolActivity(
                tool_name="generate_image", status=ToolActivityStatus.COMPLETED
            )
        return super()._parse_chunk_tool_activity(event_data)


__all__ = ["XAIResponsesStream"]
