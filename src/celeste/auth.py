"""Authentication methods for Celeste providers."""

from abc import ABC, abstractmethod
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from contextvars import ContextVar

from pydantic import BaseModel, ConfigDict, SecretStr, field_validator

from celeste.core import Modality, Operation
from celeste.exceptions import MissingAuthenticationError

# Module-level registry (same pattern as _clients and _models)
_auth_classes: dict[str, type["Authentication"]] = {}


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


# Backwards compatibility alias
APIKey = AuthHeader


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
    if auth_type not in _auth_classes:
        msg = f"Unknown auth type: {auth_type}. Available: {list(_auth_classes.keys())}"
        raise ValueError(msg)

    return _auth_classes[auth_type]


class AuthenticationContext(BaseModel):
    """Per-(modality, operation) authentication bound to an async scope."""

    # Frozen: asyncio.gather siblings share the context snapshot by reference,
    # so mutability would cause silent cross-task credential bleed.
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    entries: Mapping[tuple[Modality, Operation], Authentication | None]


_current_context: ContextVar[AuthenticationContext | None] = ContextVar(
    "celeste.auth.current_context",
    default=None,
)


@contextmanager
def authentication_scope(
    context: AuthenticationContext | None,
) -> Iterator[None]:
    """Bind an authentication context for the current async scope.

    Within the ``with`` block, calls to ``celeste.<modality>.<method>(...)``
    that don't pass an explicit ``auth=`` or ``api_key=`` resolve their
    authentication from the bound context.

    Args:
        context: The AuthenticationContext to bind, or None to clear any
            outer binding for the duration of the block.
    """
    token = _current_context.set(context)
    try:
        yield
    finally:
        _current_context.reset(token)


def resolve_authentication(
    modality: Modality, operation: Operation
) -> Authentication | None:
    """Look up (modality, operation) in the current ambient context.

    Args:
        modality: The modality to look up.
        operation: The operation to look up.

    Returns:
        The bound Authentication, or None if no ambient context is active.

    Raises:
        MissingAuthenticationError: A scope is bound but has no authentication
            for the requested (modality, operation).
    """
    context = _current_context.get()
    if context is None:
        return None
    auth = context.entries.get((modality, operation))
    if auth is None:
        raise MissingAuthenticationError(modality=modality, operation=operation)
    return auth


__all__ = [
    "APIKey",
    "AuthHeader",
    "Authentication",
    "AuthenticationContext",
    "NoAuth",
    "authentication_scope",
    "get_auth_class",
    "register_auth",
    "resolve_authentication",
]
