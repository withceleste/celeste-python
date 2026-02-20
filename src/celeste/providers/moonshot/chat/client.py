"""Moonshot Chat API client mixin."""

from typing import Any, ClassVar

from celeste.protocols.chatcompletions import ChatCompletionsClient

from . import config


class MoonshotChatClient(ChatCompletionsClient):
    """Mixin for Moonshot Chat API.

    Inherits shared Chat Completions implementation. Overrides:
    - _build_request() - Adds stream_options for usage inclusion
    """

    _default_base_url: ClassVar[str] = config.BASE_URL

    def _build_request(
        self,
        inputs: Any,
        extra_body: dict[str, Any] | None = None,
        streaming: bool = False,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Build request with model ID and streaming flag."""
        request_body = super()._build_request(
            inputs, extra_body=extra_body, streaming=streaming, **parameters
        )
        if streaming:
            request_body["stream_options"] = {"include_usage": True}
        return request_body


__all__ = ["MoonshotChatClient"]
