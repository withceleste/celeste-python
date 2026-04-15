"""Celeste - Open source, type-safe primitives for multi-modal AI."""

import logging
import warnings

from pydantic import SecretStr

from celeste import providers as _providers  # noqa: F401
from celeste.auth import (
    APIKey,
    Authentication,
    AuthenticationContext,
    AuthHeader,
    NoAuth,
    authentication_scope,
    resolve_authentication,
)
from celeste.client import ModalityClient
from celeste.core import (
    Capability,
    Modality,
    Operation,
    Protocol,
    Provider,
)
from celeste.credentials import credentials
from celeste.exceptions import (
    ClientNotFoundError,
    Error,
    MissingAuthenticationError,
    ModelNotFoundError,
)
from celeste.io import Input, Output, Usage
from celeste.modalities.audio.models import MODELS as _audio_models
from celeste.modalities.audio.providers import PROVIDERS as _audio_providers
from celeste.modalities.embeddings.models import MODELS as _embeddings_models
from celeste.modalities.embeddings.providers import PROVIDERS as _embeddings_providers
from celeste.modalities.images.models import MODELS as _images_models
from celeste.modalities.images.providers import PROVIDERS as _images_providers
from celeste.modalities.text.models import MODELS as _text_models
from celeste.modalities.text.protocols.chatcompletions import ChatCompletionsTextClient
from celeste.modalities.text.protocols.openresponses import OpenResponsesTextClient
from celeste.modalities.text.providers import PROVIDERS as _text_providers
from celeste.modalities.videos.models import MODELS as _videos_models
from celeste.modalities.videos.providers import PROVIDERS as _videos_providers
from celeste.models import Model, _models, get_model, list_models, register_models
from celeste.tools import (
    CodeExecution,
    Tool,
    ToolCall,
    ToolChoice,
    ToolResult,
    WebSearch,
    XSearch,
)
from celeste.types import Content, Message, Role

logger = logging.getLogger(__name__)

_CLIENT_MAP: dict[tuple[Modality, Provider | Protocol], type[ModalityClient]] = {
    **{(Modality.TEXT, p): c for p, c in _text_providers.items()},
    **{(Modality.IMAGES, p): c for p, c in _images_providers.items()},
    **{(Modality.VIDEOS, p): c for p, c in _videos_providers.items()},
    **{(Modality.AUDIO, p): c for p, c in _audio_providers.items()},
    **{(Modality.EMBEDDINGS, p): c for p, c in _embeddings_providers.items()},
    # Protocol entries (for compatible APIs via protocol= + base_url=)
    (Modality.TEXT, Protocol.OPENRESPONSES): OpenResponsesTextClient,
    (Modality.TEXT, Protocol.CHATCOMPLETIONS): ChatCompletionsTextClient,
}

for _model in [
    *_text_models,
    *_images_models,
    *_videos_models,
    *_audio_models,
    *_embeddings_models,
]:
    assert _model.provider is not None
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
    protocol: Protocol | None = None,
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
            # Protocol path: unregistered models are expected
            if protocol is not None:
                if modality is None:
                    msg = f"Model '{model}' not registered. Specify 'modality' explicitly."
                    raise ValueError(msg)
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
            operations = {}
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
    modality: Modality | None = None,
    operation: Operation | None = None,
    provider: Provider | None = None,
    model: Model | str | None = None,
    api_key: str | SecretStr | None = None,
    auth: Authentication | None = None,
    protocol: Protocol | None = None,
    base_url: str | None = None,
) -> ModalityClient:
    """Create an async client for the specified AI capability or modality.

    Args:
        capability: The AI capability to use (deprecated, use modality instead).
        modality: The modality to use (e.g., Modality.IMAGES, "images").
        operation: The operation to use (e.g., Operation.GENERATE, "generate").
        provider: Optional provider (e.g., Provider.OPENAI).
        model: Model object, string model ID, or None for auto-selection.
        api_key: Optional API key override (string or SecretStr).
        auth: Optional Authentication object for custom auth (e.g., GoogleADC).
            When None and api_key is also None, falls back to the ambient
            AuthenticationContext bound by ``authentication_scope(...)`` for
            the (modality, operation) pair, before the env-credential path.
        protocol: Wire format protocol for compatible APIs (e.g., "openresponses",
                  "chatcompletions"). Use with base_url for third-party compatible APIs.
        base_url: Custom base URL override. Use with protocol for compatible APIs,
                  or with provider to proxy through a custom endpoint.

    Returns:
        Configured client instance ready for generation operations.

    Raises:
        ModelNotFoundError: If no model found for the specified capability/provider.
        ClientNotFoundError: If no client registered for capability/provider/protocol.
        MissingCredentialsError: If required credentials are not configured.
        MissingAuthenticationError: If an ambient AuthenticationContext is bound
            but has no entry for the requested (modality, operation).
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

    resolved_modality = modality
    resolved_operation = operation
    resolved_provider = provider
    resolved_protocol = protocol

    # Default to openresponses when base_url is given without protocol or provider
    if base_url is not None and resolved_protocol is None and resolved_provider is None:
        resolved_protocol = Protocol.OPENRESPONSES

    resolved_model = _resolve_model(
        modality=resolved_modality,
        operation=resolved_operation,
        provider=resolved_provider,
        model=model,
        protocol=resolved_protocol,
    )

    if resolved_provider is None and resolved_protocol is None:
        resolved_provider = resolved_model.provider

    # Client lookup: protocol takes precedence for compatible API path
    target = (
        resolved_protocol if resolved_protocol is not None else resolved_model.provider
    )
    if target is None:
        raise ClientNotFoundError(modality=resolved_modality)

    if (resolved_modality, target) not in _CLIENT_MAP:
        raise ClientNotFoundError(modality=resolved_modality, provider=target)
    modality_client_class = _CLIENT_MAP[(resolved_modality, target)]

    # Ambient fallback: only when neither auth nor api_key was passed and the
    # operation is known. Explicit kwargs always win.
    if auth is None and api_key is None and resolved_operation is not None:
        auth = resolve_authentication(resolved_modality, resolved_operation)

    # Auth resolution: BYOA for protocol path, credentials for provider path
    if resolved_protocol is not None and resolved_provider is None:
        if auth is not None:
            resolved_auth = auth
        elif api_key is not None:
            resolved_auth = AuthHeader(secret=api_key)  # type: ignore[arg-type]  # validator converts str
        else:
            resolved_auth = NoAuth()
    else:
        resolved_auth = credentials.get_auth(
            resolved_model.provider,  # type: ignore[arg-type]  # always Provider in this branch
            override_auth=auth,
            override_key=api_key,
        )

    return modality_client_class(
        modality=resolved_modality,
        model=resolved_model,
        provider=resolved_provider,
        protocol=resolved_protocol,
        auth=resolved_auth,
        base_url=base_url,
    )


__all__ = [
    "APIKey",
    "Authentication",
    "AuthenticationContext",
    "Capability",
    "CodeExecution",
    "Content",
    "Error",
    "Input",
    "Message",
    "MissingAuthenticationError",
    "Modality",
    "Model",
    "Operation",
    "Output",
    "Protocol",
    "Provider",
    "Role",
    "Tool",
    "ToolCall",
    "ToolChoice",
    "ToolResult",
    "Usage",
    "WebSearch",
    "XSearch",
    "audio",
    "authentication_scope",
    "create_client",
    "documents",
    "get_model",
    "images",
    "list_models",
    "register_models",
    "text",
    "videos",
]

# Domain namespace API (imported last to avoid circular imports)
from celeste.namespaces import audio, documents, images, text, videos  # noqa: E402
