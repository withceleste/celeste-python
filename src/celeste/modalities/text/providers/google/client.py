"""Google text client dispatcher for Interactions and GenerateContent."""

from collections.abc import AsyncIterator
from typing import Any, Unpack

from celeste.grounding import Grounding
from celeste.parameters import ParameterMapper
from celeste.providers.google.auth import GoogleADC
from celeste.tools import Tool, ToolCall
from celeste.types import TextContent

from ...client import TextClient
from ...io import TextInput, TextOutput
from ...parameters import TextParameters
from ...streaming import TextStream
from .interactions import GoogleInteractionsTextClient
from .parameters import (
    GOOGLE_INTERACTIONS_PARAMETER_MAPPERS,
    GOOGLE_VERTEX_PARAMETER_MAPPERS,
)
from .vertex import GoogleVertexTextClient

# Remove with https://github.com/withceleste/celeste-python/issues/335.
_GENERATE_CONTENT_MIXED_TOOL_FALLBACK_MODELS = {
    "gemini-3.5-flash-lite",
    "gemini-3.6-flash",
}


def _has_mixed_tools(tools: object) -> bool:
    if not isinstance(tools, list):
        return False
    has_function = any(isinstance(tool, dict) and "name" in tool for tool in tools)
    has_builtin = any(
        isinstance(tool, Tool) or (isinstance(tool, dict) and "name" not in tool)
        for tool in tools
    )
    return has_function and has_builtin


class GoogleTextClient(TextClient):
    """Google text client selecting the backend by auth and request capabilities."""

    _strategy: GoogleInteractionsTextClient | GoogleVertexTextClient | None = None

    def model_post_init(self, __context: object) -> None:
        """Initialize the backend client based on auth type."""
        super().model_post_init(__context)

        StrategyClass = (
            GoogleVertexTextClient
            if isinstance(self.auth, GoogleADC)
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

    def _generate_content_fallback(
        self, tools: object
    ) -> GoogleVertexTextClient | None:
        if (
            isinstance(self._strategy, GoogleInteractionsTextClient)
            and self.model.id in _GENERATE_CONTENT_MIXED_TOOL_FALLBACK_MODELS
            and _has_mixed_tools(tools)
        ):
            return GoogleVertexTextClient(
                modality=self.modality,
                model=self.model,
                provider=self.provider,
                auth=self.auth,
                base_url=self.base_url,
            )
        return None

    async def _predict(
        self,
        inputs: TextInput,
        *,
        endpoint: str | None = None,
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextOutput:
        fallback = self._generate_content_fallback(parameters.get("tools"))
        if fallback is None:
            return await super()._predict(
                inputs,
                endpoint=endpoint,
                extra_body=extra_body,
                extra_headers=extra_headers,
                **parameters,
            )
        return await fallback._predict(
            inputs,
            endpoint=endpoint,
            extra_body=extra_body,
            extra_headers=extra_headers,
            **parameters,
        )

    def _stream(
        self,
        inputs: TextInput,
        stream_class: type[TextStream],
        *,
        endpoint: str | None = None,
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextStream:
        fallback = self._generate_content_fallback(parameters.get("tools"))
        if fallback is None:
            return super()._stream(
                inputs,
                stream_class,
                endpoint=endpoint,
                extra_body=extra_body,
                extra_headers=extra_headers,
                **parameters,
            )
        return fallback._stream(
            inputs,
            fallback._stream_class(),
            endpoint=endpoint,
            extra_body=extra_body,
            extra_headers=extra_headers,
            **parameters,
        )

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
