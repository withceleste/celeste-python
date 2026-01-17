"""Base client for modality-specific AI operations."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from json import JSONDecodeError
from typing import Any, Unpack

import httpx
from pydantic import BaseModel, ConfigDict, Field

from celeste.auth import Authentication
from celeste.core import Modality, Provider
from celeste.exceptions import StreamingNotSupportedError
from celeste.http import HTTPClient, get_http_client
from celeste.io import Chunk, FinishReason, Input, Output, Usage
from celeste.models import Model
from celeste.parameters import ParameterMapper, Parameters
from celeste.streaming import Stream
from celeste.types import TextContent


class APIMixin(ABC):
    """Abstract base for provider API mixins.

    Provider mixins inherit from this to gain type hints for ModalityClient attributes.
    The actual attributes are provided by ModalityClient through multiple inheritance.

    Layering:
        - HTTPClient: Low-level HTTP transport (requests, connection pooling)
        - APIMixin: High-level provider API logic (endpoints, request/response formats)
        - ModalityClient: Modality-specific client (text, images, audio, etc.)

    Example:
        class OpenAIResponsesMixin(APIMixin):
            async def _make_request(self, request_body, **parameters):
                request_body["model"] = self.model.id  # Type-safe!
                headers = {**self.auth.get_headers(), ...}
                return await self.http_client.post(...)

        class OpenAITextClient(OpenAIResponsesMixin, TextClient):
            pass
    """

    model: Model
    auth: Authentication
    provider: Provider

    @property
    @abstractmethod
    def http_client(self) -> HTTPClient:
        """HTTP client with connection pooling for this provider."""
        ...

    @staticmethod
    def _deep_merge(
        target: dict[str, Any],
        source: dict[str, Any],
    ) -> dict[str, Any]:
        """Deep merge source dictionary into target dictionary.

        Args:
            target: The dictionary to merge into.
            source: The dictionary to merge from.

        Returns:
            The merged dictionary (modified target).
        """
        for key, value in source.items():
            if (
                key in target
                and isinstance(target[key], dict)
                and isinstance(value, dict)
            ):
                APIMixin._deep_merge(target[key], value)
            else:
                target[key] = value
        return target

    def _build_request(
        self,
        inputs: Any,
        extra_body: dict[str, Any] | None = None,
        streaming: bool = False,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Build request dict from inputs and parameters.

        Mixins override this and call super() to chain with ModalityClient._build_request().
        """
        return super()._build_request(  # type: ignore[misc,no-any-return]
            inputs, extra_body=extra_body, streaming=streaming, **parameters
        )

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dict from response data.

        Mixins override this and call super() to chain with ModalityClient._build_metadata().
        """
        return super()._build_metadata(response_data)  # type: ignore[misc,no-any-return]

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle error responses from provider APIs.

        Stub that calls through to ModalityClient._handle_error_response via MRO.
        """
        super()._handle_error_response(response)  # type: ignore[misc]


class ModalityClient[In: Input, Out: Output, Params: Parameters, Content](
    APIMixin, BaseModel
):
    """Base class for unified modality clients.

    Operation methods in subclasses delegate to _predict().

    Example:
        class ImagesClient(ModalityClient[ImagesInput, ImagesOutput, ImagesParameters, ImageContent]):
            modality = Modality.IMAGES

            async def generate(self, prompt: str, **parameters) -> ImageGenerationOutput:
                inputs = ImageGenerationInput(prompt=prompt)
                return await self._predict(inputs, **parameters)
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    modality: Modality
    model: Model
    provider: Provider
    auth: Authentication = Field(exclude=True)

    @property
    def http_client(self) -> HTTPClient:
        """Shared HTTP client with connection pooling."""
        return get_http_client(self.provider, self.modality)

    # Namespace properties - implemented by modality clients
    @property
    def sync(self) -> Any:
        """Sync namespace for blocking operations."""
        ...

    @property
    def stream(self) -> Any:
        """Stream namespace for streaming operations."""
        ...

    async def _predict(
        self,
        inputs: In,
        *,
        endpoint: str | None = None,
        extra_body: dict[str, Any] | None = None,
        **parameters: Unpack[Params],  # type: ignore[misc]
    ) -> Out:
        """Generic prediction - called by operation methods.

        Args:
            inputs: Operation-specific input object.
            endpoint: Optional endpoint path (e.g., "/generations").
            extra_body: Additional parameters to merge into the request body.
            **parameters: Operation-specific keyword arguments.

        Returns:
            Output of the parameterized type.
        """
        inputs, parameters = self._validate_artifacts(inputs, **parameters)
        request_body = self._build_request(inputs, extra_body=extra_body, **parameters)
        response_data = await self._make_request(
            request_body, endpoint=endpoint, **parameters
        )
        return self._output_class()(
            content=self._parse_content(response_data, **parameters),
            usage=self._parse_usage(response_data),
            finish_reason=self._parse_finish_reason(response_data),
            metadata=self._build_metadata(response_data),
        )

    def _stream(
        self,
        inputs: In,
        stream_class: type[Stream[Out, Params, Chunk]],
        *,
        endpoint: str | None = None,
        base_url: str | None = None,
        extra_body: dict[str, Any] | None = None,
        **parameters: Unpack[Params],  # type: ignore[misc]
    ) -> Stream[Out, Params, Chunk]:
        """Generic streaming - called by operation methods.

        Transport-agnostic: provider implements _make_stream_request() with
        whatever transport is appropriate (HTTP SSE, WebSocket, etc.).

        Args:
            inputs: Operation-specific input object.
            stream_class: The Stream class to instantiate.
            extra_body: Additional parameters to merge into the request body.
            **parameters: Operation-specific keyword arguments.

        Returns:
            Stream yielding chunks and providing final Output.

        Raises:
            StreamingNotSupportedError: If model doesn't support streaming.
        """
        if not self.model.streaming:
            raise StreamingNotSupportedError(model_id=self.model.id)

        inputs, parameters = self._validate_artifacts(inputs, **parameters)
        request_body = self._build_request(
            inputs, extra_body=extra_body, streaming=True, **parameters
        )
        sse_iterator = self._make_stream_request(
            request_body, endpoint=endpoint, base_url=base_url, **parameters
        )
        return stream_class(
            sse_iterator,
            transform_output=self._transform_output,
            client=self,
            **parameters,
        )

    @classmethod
    @abstractmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        """Provider-specific parameter mappers."""
        ...

    @abstractmethod
    def _parse_usage(self, response_data: dict[str, Any]) -> Usage:
        """Parse usage information from provider response."""
        ...

    @abstractmethod
    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[Params],  # type: ignore[misc]
    ) -> Content:
        """Parse content from provider response."""
        ...

    def _parse_finish_reason(
        self, response_data: dict[str, Any]
    ) -> FinishReason | None:
        """Parse finish reason from provider response."""
        return None

    @classmethod
    @abstractmethod
    def _output_class(cls) -> type[Out]:
        """Return the Output class for this modality."""
        ...

    @abstractmethod
    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        **parameters: Unpack[Params],  # type: ignore[misc]
    ) -> dict[str, Any]:
        """Make HTTP request(s) and return response data."""
        ...

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[Params],  # type: ignore[misc]
    ) -> AsyncIterator[dict[str, Any]]:
        """Make HTTP streaming request and return async iterator of events."""
        raise StreamingNotSupportedError(model_id=self.model.id)

    def _stream_class(self) -> type[Stream[Out, Params, Chunk]]:
        """Return the Stream class for this client."""
        raise StreamingNotSupportedError(model_id=self.model.id)

    def _validate_artifacts(
        self,
        inputs: In,
        **parameters: Unpack[Params],  # type: ignore[misc]
    ) -> tuple[In, dict[str, Any]]:
        """Validate and prepare artifacts in inputs and parameters."""
        return inputs, parameters

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary from response data."""
        return {
            "model": self.model.id,
            "provider": self.provider,
            "modality": self.modality,
            "raw_response": response_data,
        }

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle error responses from provider APIs."""
        if not response.is_success:
            try:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", response.text)
            except JSONDecodeError:
                error_msg = response.text or f"HTTP {response.status_code}"

            raise httpx.HTTPStatusError(
                f"{self.provider} API error: {error_msg}",
                request=response.request,
                response=response,
            )

    def _transform_output(
        self,
        content: TextContent,
        **parameters: Unpack[Params],  # type: ignore[misc]
    ) -> TextContent:
        """Transform content using parameter mapper output transformations."""
        for mapper in self.parameter_mappers():
            value = parameters.get(mapper.name)
            if value is not None:
                content = mapper.parse_output(content, value)
        return content

    @abstractmethod
    def _init_request(self, inputs: In) -> dict[str, Any]:
        """Initialize provider-specific request structure from inputs."""
        ...

    def _build_request(
        self,
        inputs: In,
        extra_body: dict[str, Any] | None = None,
        streaming: bool = False,
        **parameters: Unpack[Params],  # type: ignore[misc]
    ) -> dict[str, Any]:
        """Build complete request by combining base request with parameters."""
        _ = streaming  # Passed through to provider mixins
        request = self._init_request(inputs)

        for mapper in self.parameter_mappers():
            value = parameters.get(mapper.name)
            request = mapper.map(request, value, self.model)

        if extra_body:
            self._deep_merge(request, extra_body)

        return request


__all__ = [
    "APIMixin",
    "ModalityClient",
]
