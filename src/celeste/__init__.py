"""Celeste - Open source, type-safe primitives for multi-modal AI."""

import logging
import warnings

from pydantic import SecretStr

from celeste import providers as _providers  # noqa: F401
from celeste.auth import APIKey, Authentication
from celeste.client import ModalityClient
from celeste.core import (
    Capability,
    Modality,
    Operation,
    Parameter,
    Provider,
    UsageField,
)
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
from celeste.modalities.audio.models import MODELS as _audio_models
from celeste.modalities.audio.providers import PROVIDERS as _audio_providers
from celeste.modalities.embeddings.models import MODELS as _embeddings_models
from celeste.modalities.embeddings.providers import PROVIDERS as _embeddings_providers
from celeste.modalities.images.models import MODELS as _images_models
from celeste.modalities.images.providers import PROVIDERS as _images_providers
from celeste.modalities.text.models import MODELS as _text_models
from celeste.modalities.text.providers import PROVIDERS as _text_providers
from celeste.modalities.videos.models import MODELS as _videos_models
from celeste.modalities.videos.providers import PROVIDERS as _videos_providers
from celeste.models import Model, _models, get_model, list_models, register_models
from celeste.parameters import Parameters
from celeste.structured_outputs import (
    RefResolvingJsonSchemaGenerator,
    StrictJsonSchemaGenerator,
    StrictRefResolvingJsonSchemaGenerator,
)
from celeste.types import Content, JsonValue, Message, Role
from celeste.websocket import WebSocketClient, WebSocketConnection, close_all_ws_clients

logger = logging.getLogger(__name__)

_CLIENT_MAP: dict[tuple[Modality, Provider], type[ModalityClient]] = {
    **{(Modality.TEXT, p): c for p, c in _text_providers.items()},
    **{(Modality.IMAGES, p): c for p, c in _images_providers.items()},
    **{(Modality.VIDEOS, p): c for p, c in _videos_providers.items()},
    **{(Modality.AUDIO, p): c for p, c in _audio_providers.items()},
    **{(Modality.EMBEDDINGS, p): c for p, c in _embeddings_providers.items()},
}

for _model in [
    *_text_models,
    *_images_models,
    *_videos_models,
    *_audio_models,
    *_embeddings_models,
]:
    _models[(_model.id, _model.provider)] = _model

_CAPABILITY_TO_MODALITY_OPERATION: dict[Capability, tuple[Modality, Operation]] = {
    Capability.TEXT_GENERATION: (Modality.TEXT, Operation.GENERATE),
    Capability.TEXT_EMBEDDINGS: (Modality.EMBEDDINGS, Operation.EMBED),
    Capability.IMAGE_GENERATION: (Modality.IMAGES, Operation.GENERATE),
    Capability.VIDEO_GENERATION: (Modality.VIDEOS, Operation.GENERATE),
    Capability.SPEECH_GENERATION: (Modality.AUDIO, Operation.SPEAK),
}


def _resolve_model(
    modality: Modality | None = None,
    operation: Operation | None = None,
    provider: Provider | None = None,
    model: Model | str | None = None,
) -> Model:
    """Resolve model parameter to Model object (auto-select if None, lookup if string)."""
    if model is None:
        if modality is None:
            msg = "Either 'modality' or 'model' must be provided"
            raise ValueError(msg)
        models = list_models(
            provider=provider,
            modality=modality,
            operation=operation,
        )
        if not models:
            raise ModelNotFoundError(
                modality=modality,
                provider=provider if provider else None,
            )
        return models[0]

    if isinstance(model, str):
        found = get_model(model, provider)
        if not found:
            if provider is None:
                raise ModelNotFoundError(model_id=model, provider=provider)
            if modality is None:
                msg = f"Model '{model}' not registered. Specify 'modality' explicitly."
                raise ValueError(msg)
            warnings.warn(
                f"Model '{model}' not registered in Celeste for provider {provider}. "
                "Parameter validation disabled.",
                UserWarning,
                stacklevel=3,
            )
            operations: dict[Modality, set[Operation]] = {}
            if modality is not None:
                operations[modality] = {operation} if operation else set()
            return Model(
                id=model,
                provider=provider,
                display_name=model,
                operations=operations,
                streaming=True,
            )
        return found

    return model


def _infer_operation(model: Model, modality: Modality) -> Operation:
    """Infer operation from model for a given modality. Raises if ambiguous."""
    if modality not in model.operations:
        msg = f"Model '{model.id}' does not support modality '{modality.value}'"
        raise ValueError(msg)

    operations = model.operations[modality]
    if len(operations) == 1:
        return next(iter(operations))
    if len(operations) > 1:
        ops = ", ".join(o.value for o in operations)
        msg = (
            f"Model '{model.id}' supports multiple operations for {modality.value}: {ops}. "
            "Specify 'operation' explicitly."
        )
        raise ValueError(msg)
    msg = f"Model '{model.id}' has no registered operations for modality '{modality.value}'"
    raise ValueError(msg)


def create_client(
    capability: Capability | None = None,
    modality: Modality | str | None = None,
    operation: Operation | str | None = None,
    provider: Provider | None = None,
    model: Model | str | None = None,
    api_key: str | SecretStr | None = None,
    auth: Authentication | None = None,
) -> ModalityClient:
    """Create an async client for the specified AI capability or modality.

    Args:
        capability: The AI capability to use (deprecated, use modality instead).
                    If not provided and model is specified, capability is inferred
                    from the model (if unambiguous).
        modality: The modality to use (e.g., Modality.IMAGES, "images").
                  Preferred over capability for new code.
        operation: The operation to use (e.g., Operation.GENERATE, "generate").
                   If not provided and model supports exactly one operation for the
                   modality, it is inferred automatically.
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
        ValueError: If capability/operation cannot be inferred from model.
    """
    # Translation layer: convert deprecated capability to modality/operation
    if capability is not None and modality is None:
        warnings.warn(
            "capability parameter is deprecated, use modality/operation instead",
            DeprecationWarning,
            stacklevel=2,
        )
        if capability not in _CAPABILITY_TO_MODALITY_OPERATION:
            msg = f"Unknown capability: {capability}"
            raise ValueError(msg)
        modality, operation = _CAPABILITY_TO_MODALITY_OPERATION[capability]

    if modality is None:
        msg = "Either 'modality' or 'model' must be provided"
        raise ValueError(msg)

    resolved_modality = Modality(modality) if isinstance(modality, str) else modality
    resolved_operation = (
        Operation(operation) if isinstance(operation, str) else operation
    )
    resolved_provider = Provider(provider) if isinstance(provider, str) else provider

    resolved_model = _resolve_model(
        modality=resolved_modality,
        operation=resolved_operation,
        provider=resolved_provider,
        model=model,
    )

    key = (resolved_modality, resolved_model.provider)
    if key not in _CLIENT_MAP:
        raise ClientNotFoundError(
            modality=resolved_modality, provider=resolved_model.provider
        )
    modality_client_class = _CLIENT_MAP[key]

    resolved_auth = credentials.get_auth(
        resolved_model.provider,
        override_auth=auth,
        override_key=api_key,
    )

    return modality_client_class(
        modality=resolved_modality,
        model=resolved_model,
        provider=resolved_model.provider,
        auth=resolved_auth,
    )


__all__ = [
    "APIKey",
    "Authentication",
    "Capability",
    "ClientNotFoundError",
    "ConstraintViolationError",
    "Content",
    "Error",
    "HTTPClient",
    "Input",
    "JsonValue",
    "Message",
    "MissingCredentialsError",
    "Modality",
    "ModalityClient",
    "Model",
    "ModelNotFoundError",
    "Operation",
    "Output",
    "Parameter",
    "Parameters",
    "Provider",
    "RefResolvingJsonSchemaGenerator",
    "Role",
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
    "audio",
    "close_all_http_clients",
    "close_all_ws_clients",
    "create_client",
    "get_model",
    "images",
    "list_models",
    "register_models",
    "text",
    "videos",
]

# Domain namespace API (imported last to avoid circular imports)
from celeste.namespaces import audio, images, text, videos  # noqa: E402
