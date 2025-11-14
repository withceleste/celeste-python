import logging

from pydantic import SecretStr

from celeste.client import Client, get_client_class, register_client
from celeste.core import Capability, Parameter, Provider
from celeste.credentials import credentials
from celeste.exceptions import (
    ClientNotFoundError,
    ConstraintViolationError,
    Error,
    MissingCredentialsError,
    ModelNotFoundError,
    StreamEmptyError,
    StreamingNotSupportedError,
    StreamNotExhaustedError,
    UnsupportedCapabilityError,
    UnsupportedParameterError,
    UnsupportedProviderError,
    ValidationError,
)
from celeste.http import HTTPClient, close_all_http_clients
from celeste.io import Input, Output, Usage
from celeste.models import Model, get_model, list_models, register_models
from celeste.parameters import Parameters
from celeste.registry import _load_from_entry_points

logger = logging.getLogger(__name__)


def _resolve_model(
    capability: Capability,
    provider: Provider | None,
    model: Model | str | None,
) -> Model:
    """Resolve model parameter to Model object (auto-select if None, lookup if string)."""
    if model is None:
        # Auto-select first available model
        models = list_models(provider=provider, capability=capability)
        if not models:
            raise ModelNotFoundError(
                capability=capability,
                provider=provider if provider else None,
            )
        return models[0]

    if isinstance(model, str):
        # String ID requires provider
        if not provider:
            msg = "provider required when model is a string ID"
            raise ValueError(msg)
        found = get_model(model, provider)
        if not found:
            raise ModelNotFoundError(model_id=model, provider=provider)
        return found

    return model


def create_client(
    capability: Capability,
    provider: Provider | None = None,
    model: Model | str | None = None,
    api_key: SecretStr | None = None,
) -> Client:
    """Create an async client for the specified AI capability.

    Args:
        capability: The AI capability to use (e.g., TEXT_GENERATION).
        provider: Optional provider. Required if model is a string ID.
        model: Model object, string model ID, or None for auto-selection.
        api_key: Optional SecretStr override. If not specified, loaded from environment.

    Returns:
        Configured client instance ready for generation operations.

    Raises:
        ModelNotFoundError: If no model found for the specified capability/provider.
        ClientNotFoundError: If no client registered for capability/provider.
        MissingCredentialsError: If required credentials are not configured.
        UnsupportedCapabilityError: If the resolved model doesn't support the requested capability.
    """
    # Load packages lazily when create_client is called
    _load_from_entry_points()
    # Resolve model
    resolved_model = _resolve_model(capability, provider, model)

    # Get client class and credentials
    client_class = get_client_class(capability, resolved_model.provider)
    resolved_key = credentials.get_credentials(
        resolved_model.provider, override_key=api_key
    )

    # Create and return client
    return client_class(
        model=resolved_model,
        provider=resolved_model.provider,
        capability=capability,
        api_key=resolved_key,
    )


# Exports
__all__ = [
    "Capability",
    "Client",
    "ClientNotFoundError",
    "ConstraintViolationError",
    "Error",
    "HTTPClient",
    "Input",
    "MissingCredentialsError",
    "Model",
    "ModelNotFoundError",
    "Output",
    "Parameter",
    "Parameters",
    "Provider",
    "StreamEmptyError",
    "StreamNotExhaustedError",
    "StreamingNotSupportedError",
    "UnsupportedCapabilityError",
    "UnsupportedParameterError",
    "UnsupportedProviderError",
    "Usage",
    "ValidationError",
    "close_all_http_clients",
    "create_client",
    "get_client_class",
    "get_model",
    "list_models",
    "register_client",
    "register_models",
]
