"""xAI Responses API client."""

from typing import Any, ClassVar

from celeste.io import FinishReason
from celeste.protocols.openresponses.client import OpenResponsesClient

from . import config


class XAIResponsesClient(OpenResponsesClient):
    """XAI Responses API client."""

    _default_base_url: ClassVar[str] = config.BASE_URL

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """Recognize completion even when the response contains only native output."""
        if response_data.get("status") == "completed":
            return FinishReason(reason="completed")
        return super()._parse_finish_reason(response_data)


__all__ = ["XAIResponsesClient"]
