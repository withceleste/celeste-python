"""Models and model registry for Celeste."""

from pydantic import BaseModel, Field, SerializeAsAny, computed_field

from celeste.constraints import Constraint
from celeste.core import InputType, Modality, Operation, Provider
from celeste.io import get_constraint_input_type


class Model(BaseModel):
    """Represents an AI model and its metadata."""

    id: str
    provider: Provider | None = None
    display_name: str
    operations: dict[Modality, set[Operation]] = Field(default_factory=dict)
    parameter_constraints: dict[str, SerializeAsAny[Constraint]] = Field(
        default_factory=dict
    )
    streaming: bool = Field(default=False)

    @property
    def supported_parameters(self) -> set[str]:
        """Compute supported parameter names from parameter_constraints."""
        return set(self.parameter_constraints.keys())

    @computed_field  # type: ignore[prop-decorator]
    @property
    def optional_input_types(self) -> set[InputType]:
        """Optional input types accepted via parameter_constraints."""
        types: set[InputType] = set()
        for constraint in self.parameter_constraints.values():
            input_type = get_constraint_input_type(constraint)
            if input_type is not None:
                types.add(input_type)
        return types


# Module-level registry mapping (model_id, provider) to model
_models: dict[tuple[str, Provider], Model] = {}


def register_models(
    models: Model | list[Model],
    *,
    modality: Modality | None = None,
    operation: Operation | None = None,
) -> None:
    """Register one or more models in the global registry.

    Args:
        models: Single Model instance or list of Models to register.
               Each model is indexed by (model_id, provider) tuple.
        modality: The modality these models belong to (e.g., Modality.IMAGES).
        operation: The operation these models support (e.g., Operation.GENERATE).

    Raises:
        ValueError: If display_name differs for duplicate (id, provider) pairs.
    """
    if isinstance(models, Model):
        models = [models]

    for model in models:
        if model.provider is None:
            msg = "Cannot register a model without a provider"
            raise ValueError(msg)
        key = (model.id, model.provider)

        # Get existing or create new model with empty constraints
        registered = _models.setdefault(
            key,
            Model(
                id=model.id,
                provider=model.provider,
                display_name=model.display_name,
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

        # Update constraints
        registered.parameter_constraints.update(model.parameter_constraints)

        # Merge model's pre-existing operations
        for mod, ops in model.operations.items():
            registered.operations.setdefault(mod, set()).update(ops)

        if modality is not None and operation is not None:
            registered.operations.setdefault(modality, set()).add(operation)


def get_model(model_id: str, provider: Provider | None = None) -> Model | None:
    """Get a registered model by ID, optionally filtered by provider.

    Args:
        model_id: The model identifier.
        provider: Optional provider. If None and multiple providers have the
                  model, returns the first match and emits a warning.

    Returns:
        Model instance if found, None otherwise.
    """
    if provider is not None:
        return _models.get((model_id, provider))

    # Search across all providers
    matches = [m for m in _models.values() if m.id == model_id]
    if not matches:
        return None

    if len(matches) > 1:
        import warnings

        providers = ", ".join(str(m.provider) for m in matches)
        warnings.warn(
            f"Model '{model_id}' found in multiple providers: {providers}. "
            f"Using '{matches[0].provider}'.",
            UserWarning,
            stacklevel=2,
        )

    return matches[0]


def list_models(
    provider: Provider | None = None,
    modality: Modality | None = None,
    operation: Operation | None = None,
) -> list[Model]:
    """List registered models, optionally filtered by provider, modality, or operation.

    Args:
        provider: Optional provider filter.
        modality: Optional modality filter.
        operation: Optional operation filter (requires modality).

    Returns:
        List of Model instances matching the filters.
    """
    models = list(_models.values())

    if provider is not None:
        models = [m for m in models if m.provider == provider]

    if modality is not None and operation is not None:
        # Filter by modality AND operation together
        models = [m for m in models if operation in m.operations.get(modality, set())]
    elif modality is not None:
        models = [m for m in models if modality in m.operations]
    elif operation is not None:
        models = [
            m for m in models if any(operation in ops for ops in m.operations.values())
        ]

    return models


def clear() -> None:
    """Clear all registered models from the registry."""
    _models.clear()


__all__ = ["Model", "clear", "get_model", "list_models", "register_models"]
