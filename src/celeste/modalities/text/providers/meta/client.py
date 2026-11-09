"""Meta text client (OpenResponses protocol)."""

from typing import Any, ClassVar, Unpack

from celeste.grounding import Grounding
from celeste.modalities.text.protocols.openresponses.client import (
    OpenResponsesTextClient,
)
from celeste.modalities.text.protocols.openresponses.client import (
    OpenResponsesTextStream as _OpenResponsesTextStream,
)
from celeste.parameters import ParameterMapper
from celeste.providers.meta.responses.config import BASE_URL
from celeste.types import TextContent

from ...io import TextChunk, TextInput
from ...parameters import TextParameters
from ...streaming import TextStream
from .grounding import parse_grounding
from .parameters import META_PARAMETER_MAPPERS


class MetaTextStream(_OpenResponsesTextStream):
    """Meta streaming for text modality."""

    def _aggregate_grounding(
        self, chunks: list[TextChunk], raw_events: list[dict[str, Any]]
    ) -> Grounding | None:
        """Parse cited spans and search results from response.completed data."""
        if self._response_data is None:
            return None
        return parse_grounding(self._response_data.get("output", []))


class MetaTextClient(OpenResponsesTextClient):
    """Meta - OpenResponses with default https://api.meta.ai."""

    _default_base_url: ClassVar[str] = BASE_URL

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return META_PARAMETER_MAPPERS

    def _build_request(
        self,
        inputs: TextInput,
        extra_body: dict[str, Any] | None = None,
        streaming: bool = False,
        **parameters: Unpack[TextParameters],
    ) -> dict[str, Any]:
        """Build request, asking Meta to return the results of every web search."""
        request_body = super()._build_request(
            inputs, extra_body=extra_body, streaming=streaming, **parameters
        )
        if any(
            tool.get("type") == "web_search" for tool in request_body.get("tools", [])
        ):
            include = request_body.setdefault("include", [])
            if "web_search_call.results" not in include:
                include.append("web_search_call.results")
        return request_body

    def _parse_grounding(self, response_data: dict[str, Any]) -> Grounding | None:
        """Parse cited spans and search results from Meta Responses output."""
        return parse_grounding(response_data.get("output", []))

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return MetaTextStream


__all__ = ["MetaTextClient", "MetaTextStream"]
