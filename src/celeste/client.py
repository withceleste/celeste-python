"""Base client and client registry for AI capabilities."""

from abc import ABC, abstractmethod
from typing import Any, Unpack

from pydantic import BaseModel, ConfigDict, Field, SecretStr

from celeste.core import Capability, Provider
from celeste.http import HTTPClient, get_http_client
from celeste.io import Input, Output, Usage
from celeste.models import Model
from celeste.parameters import ParameterMapper, Parameters
from celeste.streaming import Stream


class Client[In: Input, Out: Output](ABC, BaseModel):
    """Base class for all capability-specific clients."""

    model_config = ConfigDict(from_attributes=True)

    model: Model
    provider: Provider
    capability: Capability
    api_key: SecretStr = Field(exclude=True)

    def model_post_init(self, __context: object) -> None:
        """Validate capability compatibility."""
        if self.capability not in self.model.capabilities:
            raise ValueError(
                f"Model '{self.model.id}' does not support capability {self.capability.value}"
            )

    @property
    def http_client(self) -> HTTPClient:
        """Shared HTTP client with connection pooling for this provider."""
        return get_http_client(self.provider, self.capability)

    @classmethod
    @abstractmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        """Provider-specific parameter mappers."""
        ...

    @abstractmethod
    def _init_request(self, inputs: In) -> dict[str, Any]:
        """Initialize provider-specific base request structure."""
        pass

    @abstractmethod
    def _parse_usage(self, response_data: dict[str, Any]) -> Usage:
        """Parse usage information from provider response."""
        pass

    @abstractmethod
    def _parse_content(
        self, response_data: dict[str, Any], **parameters: Unpack[Parameters]
    ) -> object:
        """Parse content from provider response."""
        pass

    def _transform_output(
        self, content: object, **parameters: Unpack[Parameters]
    ) -> object:
        """Transform content using parameter mapper output transformations."""
        for mapper in self.parameter_mappers():
            value = parameters.get(mapper.name)
            if value is not None:
                content = mapper.parse_output(content, value)
        return content

    def _build_request(
        self, inputs: In, **parameters: Unpack[Parameters]
    ) -> dict[str, Any]:
        """Build complete request by combining base request with parameters."""
        request = self._init_request(inputs)

        # Apply parameter mappers from registry
        for mapper in self.parameter_mappers():
            value = parameters.get(mapper.name)
            request = mapper.map(request, value, self.model)

        return request

    def stream(self, *args: Any, **parameters: Unpack[Parameters]) -> Stream[Out]:  # noqa: ANN401
        """Stream content - signature varies by capability.

        Args:
            *args: Capability-specific positional arguments (same as generate).
            **parameters: Capability-specific keyword arguments (same as generate).

        Returns:
            Stream yielding chunks and providing final Output.

        Raises:
            NotImplementedError: If capability doesn't support streaming.
        """
        msg = f"{self.capability.value} or {self.provider.value} does not support streaming"
        raise NotImplementedError(msg)

    @abstractmethod
    async def generate(self, *args: Any, **parameters: Unpack[Parameters]) -> Out:  # noqa: ANN401
        """Generate content - signature varies by capability.

        Args:
            *args: Capability-specific positional arguments (prompt, text, image_url, etc.).
            **parameters: Capability-specific keyword arguments (temperature, max_tokens, etc.).

        Returns:
            Output of the parameterized type (e.g., TextGenerationOutput).
        """
        pass


_clients: dict[tuple[Capability, Provider], type[Client]] = {}


def register_client(
    capability: Capability, provider: Provider, client_class: type[Client]
) -> None:
    """Register a provider-specific client class for a capability.

    Args:
        capability: The capability this client implements.
        provider: The provider this client uses.
        client_class: The client class to register.
    """
    _clients[(capability, provider)] = client_class


def get_client_class(capability: Capability, provider: Provider) -> type[Client]:
    """Get the registered client class for a capability and provider.

    Args:
        capability: The capability to get a client for.
        provider: The provider to use.

    Returns:
        The registered client class.

    Raises:
        NotImplementedError: If no client is registered for this capability/provider.
    """
    if (capability, provider) not in _clients:
        raise NotImplementedError(
            f"No client registered for {capability.value} with provider {provider.value}"
        )
    return _clients[(capability, provider)]


__all__ = ["Client", "get_client_class", "register_client"]

