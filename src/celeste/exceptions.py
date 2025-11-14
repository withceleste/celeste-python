"""Custom exceptions for Celeste."""


class Error(Exception):
    """Base exception for all Celeste errors."""

    pass


class ModelError(Error):
    """Errors related to model operations and registry."""

    pass


class ModelNotFoundError(ModelError):
    """Raised when a requested model cannot be found."""

    def __init__(
        self,
        model_id: str | None = None,
        provider: str | None = None,
        capability: str | None = None,
    ) -> None:
        """Initialize with model details.

        Args:
            model_id: Optional specific model ID that was not found.
            provider: Optional provider name.
            capability: Optional capability name (used when no specific model_id).
        """
        self.model_id = model_id
        self.provider = provider
        self.capability = capability

        # Generate appropriate error message based on available parameters
        if model_id and provider:
            msg = f"Model '{model_id}' not found for provider {provider}"
        elif capability and provider:
            msg = (
                f"No model found for capability '{capability}' with provider {provider}"
            )
        elif capability:
            msg = f"No model found for capability '{capability}'"
        else:
            msg = "Model not found"

        super().__init__(msg)


class CapabilityError(Error):
    """Errors related to capability compatibility."""

    pass


class UnsupportedCapabilityError(CapabilityError):
    """Raised when a model doesn't support a requested capability."""

    def __init__(self, model_id: str, capability: str) -> None:
        """Initialize with model and capability details."""
        self.model_id = model_id
        self.capability = capability
        super().__init__(
            f"Model '{model_id}' does not support capability '{capability}'"
        )


class ClientError(Error):
    """Errors related to client operations."""

    pass


class ClientNotFoundError(ClientError):
    """Raised when no client is registered for a capability/provider combination."""

    def __init__(self, capability: str, provider: str) -> None:
        """Initialize with capability and provider details."""
        self.capability = capability
        self.provider = provider
        super().__init__(
            f"No client registered for {capability} with provider {provider}"
        )


class StreamingError(Error):
    """Errors related to streaming operations."""

    pass


class ValidationError(Error):
    """Errors related to parameter and constraint validation."""

    pass


class ConstraintViolationError(ValidationError):
    """Raised when a value violates a constraint."""

    pass


class StreamingNotSupportedError(StreamingError):
    """Raised when streaming is requested for a model that doesn't support it."""

    def __init__(self, model_id: str) -> None:
        """Initialize with model ID."""
        self.model_id = model_id
        super().__init__(f"Streaming not supported for model '{model_id}'")


class StreamNotExhaustedError(StreamingError):
    """Raised when accessing stream output before consuming all chunks."""

    def __init__(self) -> None:
        """Initialize with helpful message."""
        super().__init__(
            "Stream not exhausted. Consume all chunks before accessing .output"
        )


class StreamEmptyError(StreamingError):
    """Raised when a stream completes without producing any chunks."""

    def __init__(self) -> None:
        """Initialize with helpful message."""
        super().__init__("Stream completed but no chunks were produced")


class CredentialsError(Error):
    """Errors related to API credentials."""

    pass


class MissingCredentialsError(CredentialsError):
    """Raised when required credentials are not configured."""

    def __init__(self, provider: str) -> None:
        """Initialize with provider details."""
        self.provider = provider
        super().__init__(
            f"Provider {provider} has no credentials configured. "
            f"Set the appropriate environment variable or pass api_key parameter."
        )


class UnsupportedProviderError(CredentialsError):
    """Raised when a provider is not configured in the credential system."""

    def __init__(self, provider: str) -> None:
        """Initialize with provider details."""
        self.provider = provider
        super().__init__(
            f"Provider {provider} has no credential mapping. "
            f"This provider is not configured in the credential system."
        )


class UnsupportedParameterError(ValidationError):
    """Raised when a parameter is not supported by a model."""

    def __init__(self, parameter: str, model_id: str) -> None:
        """Initialize with parameter and model details."""
        self.parameter = parameter
        self.model_id = model_id
        super().__init__(
            f"Parameter '{parameter}' is not supported by model '{model_id}'"
        )


__all__ = [
    "ClientNotFoundError",
    "ConstraintViolationError",
    "Error",
    "MissingCredentialsError",
    "ModelNotFoundError",
    "StreamEmptyError",
    "StreamNotExhaustedError",
    "StreamingNotSupportedError",
    "UnsupportedCapabilityError",
    "UnsupportedParameterError",
    "UnsupportedProviderError",
]
