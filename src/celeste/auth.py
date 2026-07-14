"""Authentication methods for Celeste providers."""

from abc import ABC, abstractmethod

from pydantic import BaseModel, SecretStr, field_validator


class Authentication(ABC, BaseModel):
    """Base class for authentication methods."""

    @abstractmethod
    def get_headers(self) -> dict[str, str]:
        """Return authentication headers for HTTP requests."""
        ...


class AuthHeader(Authentication):
    """Authentication via HTTP header with configurable header name and prefix.

    This is the primitive for header-based authentication. Different providers
    use different header names and prefixes:
    - OpenAI: Authorization: Bearer <secret>
    - Anthropic: x-api-key: <secret>
    - Google: x-goog-api-key: <secret>
    - ElevenLabs: xi-api-key: <secret>
    """

    secret: SecretStr
    header: str = "Authorization"
    prefix: str = "Bearer "

    @field_validator("secret", mode="before")
    @classmethod
    def convert_to_secret(cls, v: str | SecretStr) -> SecretStr:
        """Accept plain strings, auto-convert to SecretStr."""
        if isinstance(v, str):
            return SecretStr(v.strip())
        return v

    def get_headers(self) -> dict[str, str]:
        """Return authentication header."""
        return {self.header: f"{self.prefix}{self.secret.get_secret_value().strip()}"}


class NoAuth(Authentication):
    """Authentication that returns no headers (local providers)."""

    def get_headers(self) -> dict[str, str]:
        """Return empty headers for unauthenticated requests."""
        return {}


__all__ = [
    "AuthHeader",
    "Authentication",
    "NoAuth",
]
