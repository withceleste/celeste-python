"""Celeste - Open source, type-safe primitives for multi-modal AI."""

import warnings

from pydantic import SecretStr

from celeste import providers as _providers  # noqa: F401
from celeste.auth import Authentication, AuthHeader, NoAuth
from celeste.client import ModalityClient
from celeste.core import Modality, Operation, Protocol, Provider
from celeste.credentials import credentials
from celeste.exceptions import (
    ClientNotFoundError,
    Error,
    ModelNotFoundError,
)
from celeste.io import Input, Output, Usage
from celeste.modalities.audio.models import MODELS as _audio_models
from celeste.modalities.audio.providers import PROVIDERS as _audio_providers
from celeste.modalities.embeddings.models import MODELS as _embeddings_models
from celeste.modalities.embeddings.providers import PROVIDERS as _embeddings_providers
from celeste.modalities.images.models import MODELS as _images_models
from celeste.modalities.images.providers import PROVIDERS as _images_providers
from celeste.modalities.segmentation.models import MODELS as _segmentation_models
from celeste.modalities.segmentation.providers import (
    PROVIDERS as _segmentation_providers,
)
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
    ToolError,
    ToolOutput,
    ToolResult,
    WebSearch,
    XSearch,
)
from celeste.types import (
    AudioPart,
    DocumentPart,
    ImagePart,
    Message,
    MessageContent,
    MessagePart,
    Role,
    TextPart,
    ToolResultContent,
    VideoPart,
)

_CLIENT_MAP: dict[tuple[Modality, Provider | Protocol], type[ModalityClient]] = {
    **{(Modality.TEXT, p): c for p, c in _text_providers.items()},
    **{(Modality.IMAGES, p): c for p, c in _images_providers.items()},
    **{(Modality.VIDEOS, p): c for p, c in _videos_providers.items()},
    **{(Modality.AUDIO, p): c for p, c in _audio_providers.items()},
    **{(Modality.EMBEDDINGS, p): c for p, c in _embeddings_providers.items()},
    **{(Modality.SEGMENTATION, p): c for p, c in _segmentation_providers.items()},
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
    *_segmentation_models,
]:
    assert _model.provider is not None
    _models[(_model.id, _model.provider)] = _model


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
            if protocol is None and provider is None:
                raise ModelNotFoundError(model_id=model)
            if modality is None:
                msg = f"Model '{model}' not registered. Specify 'modality' explicitly."
                raise ValueError(msg)
            if protocol is None:
                warnings.warn(
                    f"Model '{model}' not registered in Celeste for provider {provider}. "
                    "Parameter validation disabled.",
                    UserWarning,
                    stacklevel=3,
                )
            return Model(
                id=model,
                provider=provider,
                display_name=model,
                operations={modality: {operation} if operation else set()},
                streaming=True,
            )
        return found

    return model


def create_client(
    modality: Modality | None = None,
    operation: Operation | None = None,
    provider: Provider | None = None,
    model: Model | str | None = None,
    api_key: str | SecretStr | None = None,
    auth: Authentication | None = None,
    protocol: Protocol | None = None,
    base_url: str | None = None,
) -> ModalityClient:
    """Create an async client for the specified modality.

    Args:
        modality: The modality to use (e.g., Modality.IMAGES, "images").
        operation: The operation to use (e.g., Operation.GENERATE, "generate").
        provider: Optional provider (e.g., Provider.OPENAI).
        model: Model object, string model ID, or None for auto-selection.
        api_key: Optional API key override (string or SecretStr).
        auth: Optional Authentication object for custom auth (e.g., GoogleADC).
        protocol: Wire format protocol for compatible APIs (e.g., "openresponses",
                  "chatcompletions"). Use with base_url for third-party compatible APIs.
        base_url: Custom base URL override. Use with protocol for compatible APIs,
                  or with provider to proxy through a custom endpoint.

    Returns:
        Configured client instance ready for generation operations.

    Raises:
        ModelNotFoundError: If no model is found for the specified modality/provider.
        ClientNotFoundError: If no client is registered for the modality/target.
        MissingCredentialsError: If required credentials are not configured.
        ValueError: If neither a modality nor enough model context is provided.
    """
    if modality is None:
        msg = "'modality' must be provided"
        raise ValueError(msg)

    # Default to openresponses when base_url is given without protocol or provider
    if base_url is not None and protocol is None and provider is None:
        protocol = Protocol.OPENRESPONSES

    resolved_model = _resolve_model(
        modality=modality,
        operation=operation,
        provider=provider,
        model=model,
        protocol=protocol,
    )

    if provider is None and protocol is None:
        provider = resolved_model.provider

    # Client lookup: protocol takes precedence for compatible API path
    target = protocol if protocol is not None else resolved_model.provider
    if target is None:
        raise ClientNotFoundError(modality=modality)

    if (modality, target) not in _CLIENT_MAP:
        raise ClientNotFoundError(modality=modality, provider=target)
    modality_client_class = _CLIENT_MAP[(modality, target)]

    # Auth resolution: BYOA for protocol path, credentials for provider path
    if protocol is not None and provider is None:
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
        modality=modality,
        model=resolved_model,
        provider=provider,
        protocol=protocol,
        auth=resolved_auth,
        base_url=base_url,
    )


__all__ = [
    "AudioPart",
    "Authentication",
    "CodeExecution",
    "DocumentPart",
    "Error",
    "ImagePart",
    "Input",
    "Message",
    "MessageContent",
    "MessagePart",
    "Modality",
    "Model",
    "Operation",
    "Output",
    "Protocol",
    "Provider",
    "Role",
    "TextPart",
    "Tool",
    "ToolCall",
    "ToolChoice",
    "ToolError",
    "ToolOutput",
    "ToolResult",
    "ToolResultContent",
    "Usage",
    "VideoPart",
    "WebSearch",
    "XSearch",
    "audio",
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
