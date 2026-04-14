"""Ambient authentication scope keyed by (modality, operation)."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from contextvars import ContextVar

from pydantic import BaseModel, ConfigDict

from celeste.auth import Authentication
from celeste.core import Modality, Operation
from celeste.exceptions import MissingAuthenticationError


class AuthenticationContext(BaseModel):
    """Per-(modality, operation) authentication bound to an async scope."""

    # Frozen: asyncio.gather siblings share the context snapshot by reference,
    # so mutability would cause silent cross-task credential bleed.
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    entries: Mapping[tuple[Modality, Operation], Authentication | None]

    def get_for(
        self, modality: Modality, operation: Operation
    ) -> Authentication | None:
        """Return the authentication for a given (modality, operation)."""
        return self.entries.get((modality, operation))


_current_context: ContextVar[AuthenticationContext | None] = ContextVar(
    "celeste.authentication_context.current",
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

    Returns ``None`` when no scope is bound (caller may fall back to env).
    Raises ``MissingAuthenticationError`` when a scope is bound but has no
    authentication for the requested (modality, operation) — the caller
    explicitly scoped auth and this slot is uncovered.
    """
    context = _current_context.get()
    if context is None:
        return None
    auth = context.get_for(modality, operation)
    if auth is None:
        raise MissingAuthenticationError(modality=modality, operation=operation)
    return auth


__all__ = [
    "AuthenticationContext",
    "authentication_scope",
    "resolve_authentication",
]
