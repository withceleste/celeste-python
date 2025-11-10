"""Models and model registry for Celeste."""

from pydantic import BaseModel, Field

from celeste.constraints import Constraint
from celeste.core import Capability, Provider


class Model(BaseModel):
    """Represents an AI model with its capabilities and metadata."""

    id: str
    provider: Provider
    display_name: str
    capabilities: set[Capability] = Field(default_factory=set)
    parameter_constraints: dict[str, Constraint] = Field(default_factory=dict)
    streaming: bool = Field(default=False)

    @property
    def supported_parameters(self) -> set[str]:
        """Compute supported parameter names from parameter_constraints."""
        return set(self.parameter_constraints.keys())


# Module-level registry mapping (model_id, provider) to model
_models: dict[tuple[str, Provider], Model] = {}


def register_models(models: Model | list[Model], capability: Capability) -> None:
    """Register one or more models in the global registry.

    Args:
        models: Single Model instance or list of Models to register.
               Each model is indexed by (model_id, provider) tuple.
        capability: The capability these models are being registered for.

    Raises:
        ValueError: If display_name differs for duplicate (id, provider) pairs.
    """
    if isinstance(models, Model):
        models = [models]

    for model in models:
        key = (model.id, model.provider)

        # Get existing or create new model with empty capabilities/constraints
        registered = _models.setdefault(
            key,
            Model(
                id=model.id,
                provider=model.provider,
                display_name=model.display_name,
                capabilities=set(),
                parameter_constraints={},
                streaming=model.streaming,
            ),
        )

        # Validate display name consistency
        if registered.display_name != model.display_name:
            raise ValueError(
                f"Inconsistent display_name for {model.id}: "
                f"'{registered.display_name}' vs '{model.display_name}'"
            )

        # Update capabilities and constraints (single code path)
        registered.capabilities.add(capability)
        registered.parameter_constraints.update(model.parameter_constraints)


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
    # Load packages lazily to avoid circular imports
    from celeste.registry import _load_from_entry_points

    _load_from_entry_points()
    models = list(_models.values())

    if provider is not None:
        models = [m for m in models if m.provider == provider]

    if capability is not None:
        models = [m for m in models if capability in m.capabilities]

    return models


def clear() -> None:
    """Clear all registered models from the registry."""
    _models.clear()


__all__ = ["Model", "clear", "get_model", "list_models", "register_models"]
