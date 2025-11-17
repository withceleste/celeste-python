"""Base client and client registry for AI capabilities."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from json import JSONDecodeError
from typing import Any, Unpack

import httpx
from pydantic import BaseModel, ConfigDict, Field, SecretStr

from celeste.core import Capability, Provider
from celeste.exceptions import (
    ClientNotFoundError,
    StreamingNotSupportedError,
    UnsupportedCapabilityError,
)
from celeste.http import HTTPClient, get_http_client
from celeste.io import Chunk, FinishReason, Input, Output, Usage
from celeste.models import Model
from celeste.parameters import ParameterMapper, Parameters
from celeste.streaming import Stream


class Client[In: Input, Out: Output, Params: Parameters](ABC, BaseModel):
    """Base class for all capability-specific clients."""

    model_config = ConfigDict(from_attributes=True)

    model: Model
    provider: Provider
    capability: Capability
    api_key: SecretStr = Field(exclude=True)

    def model_post_init(self, __context: object) -> None:
        """Validate capability compatibility."""
        if self.capability not in self.model.capabilities:
            raise UnsupportedCapabilityError(
                model_id=self.model.id,
                capability=self.capability,
            )

    @property
    def http_client(self) -> HTTPClient:
        """Shared HTTP client with connection pooling for this provider."""
        return get_http_client(self.provider, self.capability)

    async def generate(
        self,
        *args: Any,  # noqa: ANN401
        **parameters: Unpack[Params],  # type: ignore[misc]
    ) -> Out:
        """Generate content - signature varies by capability.

        Args:
            *args: Capability-specific positional arguments (prompt, image, video, etc.).
            **parameters: Capability-specific keyword arguments (temperature, max_tokens, etc.).

        Returns:
            Output of the parameterized type (e.g., TextGenerationOutput).
        """
        inputs = self._create_inputs(*args, **parameters)
        inputs, parameters = self._validate_artifacts(inputs, **parameters)
        request_body = self._build_request(inputs, **parameters)
        response = await self._make_request(request_body, **parameters)
        self._handle_error_response(response)
        response_data = response.json()
        return self._output_class()(
            content=self._parse_content(response_data, **parameters),
            usage=self._parse_usage(response_data),
            finish_reason=self._parse_finish_reason(response_data),
            metadata=self._build_metadata(response_data),
        )

    def stream(
        self,
        *args: Any,  # noqa: ANN401
        **parameters: Unpack[Params],  # type: ignore[misc]
    ) -> Stream[Out, Params, Chunk]:
        """Stream content - signature varies by capability.

        Args:
            *args: Capability-specific positional arguments (same as generate).
            **parameters: Capability-specific keyword arguments (same as generate).

        Returns:
            Stream yielding chunks and providing final Output.

        Raises:
            StreamingNotSupportedError: If model doesn't support streaming.
        """
        if not self.model.streaming:
            raise StreamingNotSupportedError(model_id=self.model.id)

        inputs = self._create_inputs(*args, **parameters)
        inputs, parameters = self._validate_artifacts(inputs, **parameters)
        request_body = self._build_request(inputs, **parameters)
        sse_iterator = self._make_stream_request(request_body, **parameters)
        return self._stream_class()(
            sse_iterator,
            transform_output=self._transform_output,
            **parameters,
        )

    @classmethod
    @abstractmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        """Provider-specific parameter mappers."""
        ...

    @abstractmethod
    def _init_request(self, inputs: In) -> dict[str, Any]:
        """Initialize provider-specific base request structure."""
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
    ) -> object:
        """Parse content from provider response."""
        ...

    def _parse_finish_reason(
        self, response_data: dict[str, Any]
    ) -> FinishReason | None:
        """Parse finish reason from provider response.

        Default implementation returns None. Override in capability-specific
        clients that support finish reasons (e.g., text-generation, image-generation).
        """
        return None

    @abstractmethod
    def _create_inputs(
        self,
        *args: Any,  # noqa: ANN401
        **parameters: Unpack[Params],  # type: ignore[misc]
    ) -> In:
        """Map positional arguments to Input type."""
        ...

    @classmethod
    @abstractmethod
    def _output_class(cls) -> type[Out]:
        """Return the Output class for this client."""
        ...

    @abstractmethod
    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[Params],  # type: ignore[misc]
    ) -> httpx.Response:
        """Make HTTP request(s) and return response object."""
        ...

    def _stream_class(self) -> type[Stream[Out, Params, Chunk]]:
        """Return the Stream class for this client."""
        raise StreamingNotSupportedError(model_id=self.model.id)

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[Params],  # type: ignore[misc]
    ) -> AsyncIterator[dict[str, Any]]:
        """Make HTTP streaming request and return async iterator of events."""
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
        content: object,
        **parameters: Unpack[Params],  # type: ignore[misc]
    ) -> object:
        """Transform content using parameter mapper output transformations."""
        for mapper in self.parameter_mappers():
            value = parameters.get(mapper.name)
            if value is not None:
                content = mapper.parse_output(content, value)
        return content

    def _build_request(
        self,
        inputs: In,
        **parameters: Unpack[Params],  # type: ignore[misc]
    ) -> dict[str, Any]:
        """Build complete request by combining base request with parameters."""
        request = self._init_request(inputs)

        for mapper in self.parameter_mappers():
            value = parameters.get(mapper.name)
            request = mapper.map(request, value, self.model)

        return request


_clients: dict[tuple[Capability, Provider], type[Client[Any, Any, Any]]] = {}


def register_client(
    capability: Capability,
    provider: Provider,
    client_class: type[Client[Any, Any, Any]],
) -> None:
    """Register a provider-specific client class for a capability.

    Args:
        capability: The capability this client implements.
        provider: The provider this client uses.
        client_class: The client class to register.
    """
    _clients[(capability, provider)] = client_class


def get_client_class(
    capability: Capability, provider: Provider
) -> type[Client[Any, Any, Any]]:
    """Get the registered client class for a capability and provider.

    Args:
        capability: The capability to get a client for.
        provider: The provider to use.

    Returns:
        The registered client class.

    Raises:
        ClientNotFoundError: If no client is registered for this capability/provider.
    """
    if (capability, provider) not in _clients:
        raise ClientNotFoundError(
            capability=capability,
            provider=provider,
        )
    return _clients[(capability, provider)]


__all__ = ["Client", "get_client_class", "register_client"]
