"""Models and model registry for Celeste."""

from pydantic import BaseModel, Field

from celeste.constraints import Constraint
from celeste.core import Capability, Provider


class Model(BaseModel):
    """Represents an AI model with its capabilities and metadata."""

    id: str
    provider: Provider
    capabilities: set[Capability] = Field(default_factory=set)
    display_name: str
    parameter_constraints: dict[str, Constraint] = Field(default_factory=dict)

    @property
    def supported_parameters(self) -> set[str]:
        """Compute supported parameter names from parameter_constraints."""
        return set(self.parameter_constraints.keys())


# Module-level registry mapping (model_id, provider) to model
_models: dict[tuple[str, Provider], Model] = {}


def register_models(models: Model | list[Model]) -> None:
    """Register one or more models in the global registry.

    Args:
        models: Single Model instance or list of Models to register.
               Each model is indexed by (model_id, provider) tuple.

    Raises:
        ValueError: If a model with the same (id, provider) is already registered.
    """
    if isinstance(models, Model):
        models = [models]

    for model in models:
        key = (model.id, model.provider)
        if key in _models:
            msg = f"Model '{model.id}' for provider {model.provider.value} is already registered"
            raise ValueError(msg)
        _models[key] = model


def get_model(model_id: str, provider: Provider) -> Model | None:
    """Get a registered model by ID and provider.

    Args:
        model_id: The model identifier.
        provider: The provider that owns the model.

    Returns:
        Model instance if found, None otherwise.
    """
    return _models.get((model_id, provider))


def list_models(
    provider: Provider | None = None,
    capability: Capability | None = None,
) -> list[Model]:
    """List all registered models, optionally filtered by provider and/or capability.

    Args:
        provider: Optional provider filter. If provided, only models from this provider are returned.
        capability: Optional capability filter. If provided, only models supporting this capability are returned.

    Returns:
        List of Model instances matching the filters.
    """
    filtered = list(_models.values())

    if provider is not None:
        filtered = [m for m in filtered if m.provider == provider]

    if capability is not None:
        filtered = [m for m in filtered if capability in m.capabilities]

    return filtered


def clear() -> None:
    """Clear all registered models from the registry."""
    _models.clear()


__all__ = ["Model", "clear", "get_model", "list_models", "register_models"]
