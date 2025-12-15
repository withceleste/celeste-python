"""Authentication methods for Celeste providers."""

from abc import ABC, abstractmethod

from pydantic import BaseModel, SecretStr, field_validator

# Module-level registry (same pattern as _clients and _models)
_auth_classes: dict[str, type["Authentication"]] = {}


class Authentication(ABC, BaseModel):
    """Base class for authentication methods."""

    @abstractmethod
    def get_headers(self) -> dict[str, str]:
        """Return authentication headers for HTTP requests."""
        ...


class APIKey(Authentication):
    """API key authentication.

    Supports configurable header name and prefix for different provider formats:
    - OpenAI: Authorization: Bearer <key>
    - Anthropic: x-api-key: <key>
    - Google: x-goog-api-key: <key>
    - ElevenLabs: xi-api-key: <key>
    """

    key: SecretStr
    header: str = "Authorization"
    prefix: str = "Bearer "

    @field_validator("key", mode="before")
    @classmethod
    def convert_to_secret(cls, v: str | SecretStr) -> SecretStr:
        """Accept plain strings, auto-convert to SecretStr."""
        if isinstance(v, str):
            return SecretStr(v)
        return v

    def get_headers(self) -> dict[str, str]:
        """Return API key authentication header."""
        return {self.header: f"{self.prefix}{self.key.get_secret_value()}"}


def register_auth(auth_type: str, auth_class: type[Authentication]) -> None:
    """Register an authentication class.

    Args:
        auth_type: The auth type identifier (e.g., "google_adc").
        auth_class: The Authentication subclass to register.
    """
    _auth_classes[auth_type] = auth_class


def get_auth_class(auth_type: str) -> type[Authentication]:
    """Get a registered authentication class by type.

    Args:
        auth_type: The auth type identifier.

    Returns:
        The registered Authentication subclass.

    Raises:
        ValueError: If auth type is not registered.
    """
    from celeste.registry import _load_providers_from_entry_points

    _load_providers_from_entry_points()

    if auth_type not in _auth_classes:
        msg = f"Unknown auth type: {auth_type}. Available: {list(_auth_classes.keys())}"
        raise ValueError(msg)

    return _auth_classes[auth_type]


__all__ = ["APIKey", "Authentication", "get_auth_class", "register_auth"]
