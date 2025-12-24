import logging
import warnings

from pydantic import SecretStr

from celeste.auth import APIKey, Authentication
from celeste.client import Client, get_client_class, register_client
from celeste.core import Capability, Parameter, Provider, UsageField
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
from celeste.io import Input, Output, Usage, get_input_class, register_input
from celeste.models import Model, get_model, list_models, register_models
from celeste.parameters import Parameters
from celeste.registry import _load_from_entry_points
from celeste.structured_outputs import (
    RefResolvingJsonSchemaGenerator,
    StrictJsonSchemaGenerator,
    StrictRefResolvingJsonSchemaGenerator,
)
from celeste.types import JsonValue
from celeste.utils import image_to_data_uri
from celeste.websocket import WebSocketClient, WebSocketConnection, close_all_ws_clients

logger = logging.getLogger(__name__)


def _infer_capability(model: Model) -> Capability:
    """Infer capability from model. Raises if ambiguous."""
    if len(model.capabilities) == 1:
        return next(iter(model.capabilities))
    if len(model.capabilities) > 1:
        caps = ", ".join(c.value for c in model.capabilities)
        msg = f"Model '{model.id}' supports multiple capabilities: {caps}. Specify 'capability' explicitly."
        raise ValueError(msg)
    msg = f"Model '{model.id}' has no registered capabilities"
    raise ValueError(msg)


def _resolve_model(
    capability: Capability | None,
    provider: Provider | None,
    model: Model | str | None,
) -> Model:
    """Resolve model parameter to Model object (auto-select if None, lookup if string)."""
    if model is None:
        if capability is None:
            msg = "Either 'capability' or 'model' must be provided"
            raise ValueError(msg)
        # Auto-select first available model
        models = list_models(provider=provider, capability=capability)
        if not models:
            raise ModelNotFoundError(
                capability=capability,
                provider=provider if provider else None,
            )
        return models[0]

    if isinstance(model, str):
        found = get_model(model, provider)
        if not found:
            if provider is None:
                raise ModelNotFoundError(model_id=model, provider=provider)
            if capability is None:
                msg = (
                    f"Model '{model}' not registered. Specify 'capability' explicitly."
                )
                raise ValueError(msg)
            warnings.warn(
                f"Model '{model}' not registered in Celeste for provider {provider.value}. "
                "Parameter validation disabled.",
                UserWarning,
                stacklevel=3,
            )
            return Model(
                id=model,
                provider=provider,
                display_name=model,
                capabilities={capability},
                streaming=True,
            )
        return found

    return model


def create_client(
    capability: Capability | None = None,
    provider: Provider | None = None,
    model: Model | str | None = None,
    api_key: str | SecretStr | None = None,
    auth: Authentication | None = None,
) -> Client:
    """Create an async client for the specified AI capability.

    Args:
        capability: The AI capability to use. If not provided and model is specified,
                    capability is inferred from the model (if unambiguous).
        provider: Optional provider. If not specified and model ID matches multiple
                  providers, the first match is used with a warning.
        model: Model object, string model ID, or None for auto-selection.
        api_key: Optional API key override (string or SecretStr).
        auth: Optional Authentication object for custom auth (e.g., GoogleADC).

    Returns:
        Configured client instance ready for generation operations.

    Raises:
        ModelNotFoundError: If no model found for the specified capability/provider.
        ClientNotFoundError: If no client registered for capability/provider.
        MissingCredentialsError: If required credentials are not configured.
        UnsupportedCapabilityError: If the resolved model doesn't support the requested capability.
        ValueError: If capability cannot be inferred from model.
    """
    # Load packages lazily when create_client is called
    _load_from_entry_points()
    # Resolve model
    resolved_model = _resolve_model(capability, provider, model)

    # Infer capability if not provided
    resolved_capability = (
        capability if capability else _infer_capability(resolved_model)
    )

    # Get client class and authentication
    client_class = get_client_class(resolved_capability, resolved_model.provider)
    resolved_auth = credentials.get_auth(
        resolved_model.provider,
        override_auth=auth,
        override_key=api_key,
    )

    # Create and return client
    return client_class(
        model=resolved_model,
        provider=resolved_model.provider,
        capability=resolved_capability,
        auth=resolved_auth,
    )


# Exports
__all__ = [
    "APIKey",
    "Authentication",
    "Capability",
    "Client",
    "ClientNotFoundError",
    "ConstraintViolationError",
    "Error",
    "HTTPClient",
    "Input",
    "JsonValue",
    "MissingCredentialsError",
    "Model",
    "ModelNotFoundError",
    "Output",
    "Parameter",
    "Parameters",
    "Provider",
    "RefResolvingJsonSchemaGenerator",
    "StreamEmptyError",
    "StreamNotExhaustedError",
    "StreamingNotSupportedError",
    "StrictJsonSchemaGenerator",
    "StrictRefResolvingJsonSchemaGenerator",
    "UnsupportedCapabilityError",
    "UnsupportedParameterError",
    "UnsupportedProviderError",
    "Usage",
    "UsageField",
    "ValidationError",
    "WebSocketClient",
    "WebSocketConnection",
    "close_all_http_clients",
    "close_all_ws_clients",
    "create_client",
    "get_client_class",
    "get_input_class",
    "get_model",
    "image_to_data_uri",
    "list_models",
    "register_client",
    "register_input",
    "register_models",
]
