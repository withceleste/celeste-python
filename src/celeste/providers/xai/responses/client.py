"""xAI Responses API client."""

from typing import Any, ClassVar

from celeste.io import FinishReason
from celeste.protocols.openresponses.client import OpenResponsesClient

from . import config


class XAIResponsesClient(OpenResponsesClient):
    """XAI Responses API client."""

    _default_base_url: ClassVar[str] = config.BASE_URL

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """Recognize completed responses even when they contain only tool output."""
        if response_data.get("status") == "completed":
            return FinishReason(reason="completed")
        return super()._parse_finish_reason(response_data)

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | float | None]:
        """Map xAI Responses usage, including context-compaction telemetry."""
        usage = OpenResponsesClient.map_usage_fields(usage_data)
        usage["dropped_message_count"] = usage_data.get("dropped_message_count")
        return usage


__all__ = ["XAIResponsesClient"]
