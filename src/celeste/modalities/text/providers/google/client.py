"""Google text client (Interactions API; GoogleADC auth uses Vertex GenerateContent)."""

from collections.abc import AsyncIterator
from typing import Any, Unpack

from celeste.grounding import Grounding
from celeste.parameters import ParameterMapper
from celeste.providers.google.auth import GoogleADC
from celeste.tools import ToolCall
from celeste.types import TextContent

from ...client import TextClient
from ...io import TextInput
from ...parameters import TextParameters
from ...streaming import TextStream
from .interactions import GoogleInteractionsTextClient
from .parameters import (
    GOOGLE_INTERACTIONS_PARAMETER_MAPPERS,
    GOOGLE_VERTEX_PARAMETER_MAPPERS,
)
from .vertex import GoogleVertexTextClient

# Interactions rejects mixing built-in tools with function calling for these ids and
# does not accept tool_config.include_server_side_tool_invocations; GenerateContent
# accepts the mix when includeServerSideToolInvocations is set (ToolsMapper).
_GENERATE_CONTENT_API_KEY_MODELS = frozenset(
    {
        "gemini-3.5-flash-lite",
        "gemini-3.6-flash",
    }
)


class GoogleTextClient(TextClient):
    """Google text client (selects the Interactions or Vertex backend by auth)."""

    _strategy: GoogleInteractionsTextClient | GoogleVertexTextClient | None = None

    def model_post_init(self, __context: object) -> None:
        """Initialize the backend client based on auth type."""
        super().model_post_init(__context)

        use_generate_content = isinstance(self.auth, GoogleADC) or (
            self.model.id in _GENERATE_CONTENT_API_KEY_MODELS
        )
        StrategyClass = (
            GoogleVertexTextClient
            if use_generate_content
            else GoogleInteractionsTextClient
        )
        strategy = StrategyClass(
            modality=self.modality,
            model=self.model,
            provider=self.provider,
            auth=self.auth,
            base_url=self.base_url,
        )
        object.__setattr__(self, "_strategy", strategy)

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return [
            *GOOGLE_INTERACTIONS_PARAMETER_MAPPERS,
            *GOOGLE_VERTEX_PARAMETER_MAPPERS,
        ]

    def _init_request(self, inputs: TextInput) -> dict[str, Any]:
        return self._strategy._init_request(inputs)  # type: ignore[union-attr]

    def _build_request(
        self,
        inputs: TextInput,
        extra_body: dict[str, Any] | None = None,
        streaming: bool = False,
        **parameters: Unpack[TextParameters],
    ) -> dict[str, Any]:
        return self._strategy._build_request(  # type: ignore[union-attr]
            inputs, extra_body=extra_body, streaming=streaming, **parameters
        )

    def _transform_output(
        self, content: TextContent, **parameters: Unpack[TextParameters]
    ) -> TextContent:
        return self._strategy._transform_output(content, **parameters)  # type: ignore[union-attr]

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        return self._strategy._build_metadata(response_data)  # type: ignore[union-attr]

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        return self._strategy._parse_usage(response_data)  # type: ignore[union-attr]

    def _parse_content(self, response_data: dict[str, Any]) -> TextContent:
        return self._strategy._parse_content(response_data)  # type: ignore[union-attr]

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> Any:
        return self._strategy._parse_finish_reason(response_data)  # type: ignore[union-attr]

    def _parse_reasoning(
        self, response_data: dict[str, Any]
    ) -> tuple[str | None, list[dict[str, Any]]]:
        return self._strategy._parse_reasoning(response_data)  # type: ignore[union-attr]

    def _parse_grounding(self, response_data: dict[str, Any]) -> Grounding | None:
        return self._strategy._parse_grounding(response_data)  # type: ignore[union-attr]

    def _parse_tool_calls(self, response_data: dict[str, Any]) -> list[ToolCall]:
        return self._strategy._parse_tool_calls(response_data)  # type: ignore[union-attr]

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[TextParameters],
    ) -> dict[str, Any]:
        return await self._strategy._make_request(  # type: ignore[union-attr]
            request_body,
            endpoint=endpoint,
            extra_headers=extra_headers,
            **parameters,
        )

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[TextParameters],
    ) -> AsyncIterator[dict[str, Any]]:
        return self._strategy._make_stream_request(  # type: ignore[union-attr]
            request_body,
            endpoint=endpoint,
            extra_headers=extra_headers,
            **parameters,
        )

    def _stream_class(self) -> type[TextStream]:
        return self._strategy._stream_class()  # type: ignore[union-attr]


__all__ = ["GoogleTextClient"]
