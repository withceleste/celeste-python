import importlib.metadata
import logging

from pydantic import SecretStr

from celeste.client import Client, get_client_class, register_client
from celeste.core import Capability, Parameter, Provider
from celeste.credentials import credentials
from celeste.http import HTTPClient, close_all_http_clients
from celeste.io import Input, Output, Usage
from celeste.models import Model, get_model, list_models, register_models
from celeste.parameters import Parameters

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
            msg = f"No model found for {capability}"
            raise ValueError(msg)
        return models[0]

    if isinstance(model, str):
        # String ID requires provider
        if not provider:
            msg = "provider required when model is a string ID"
            raise ValueError(msg)
        found = get_model(model, provider)
        if not found:
            msg = f"Model '{model}' not found for provider {provider}"
            raise ValueError(msg)
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
        ValueError: If no model found or resolution fails.
        NotImplementedError: If no client registered for capability/provider.
    """
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


def _load_from_entry_points() -> None:
    """Load models and clients from installed packages via entry points."""
    entry_points = importlib.metadata.entry_points(group="celeste.packages")

    for ep in entry_points:
        register_func = ep.load()
        # The function should register models and clients when called
        register_func()


# Load from entry points on import
_load_from_entry_points()

# Exports
__all__ = [
    "Capability",
    "Client",
    "HTTPClient",
    "Input",
    "Model",
    "Output",
    "Parameter",
    "Parameters",
    "Provider",
    "Usage",
    "close_all_http_clients",
    "create_client",
    "get_client_class",
    "get_model",
    "list_models",
    "register_client",
    "register_models",
]
