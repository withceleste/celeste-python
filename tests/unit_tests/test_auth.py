"""Tests for authentication classes, registry, and ambient scope."""

import asyncio
import contextvars
from collections.abc import Generator
from concurrent.futures import ThreadPoolExecutor

import pytest
from pydantic import SecretStr, ValidationError

from celeste.auth import (
    APIKey,
    Authentication,
    AuthenticationContext,
    AuthHeader,
    NoAuth,
    authentication_scope,
    get_auth_class,
    register_auth,
    resolve_authentication,
)
from celeste.core import Provider
from celeste.exceptions import MissingAuthenticationError


@pytest.fixture(autouse=True)
def clean_auth_registry() -> Generator[None, None, None]:
    """Clear auth registry before and after each test to ensure isolation.

    Tests must not depend on provider package import side-effects.
    """
    import importlib

    auth_module = importlib.import_module("celeste.auth")

    # Store original state
    original_auth_classes = auth_module._auth_classes.copy()

    # Clear before test
    auth_module._auth_classes.clear()

    yield

    # Clear after test
    auth_module._auth_classes.clear()
    # Restore original state (in case tests registered something)
    auth_module._auth_classes.update(original_auth_classes)


class TestAuthHeader:
    """Test AuthHeader authentication class."""

    def test_convert_to_secret_with_string(self) -> None:
        """Test that convert_to_secret converts plain string to SecretStr."""
        auth = AuthHeader(secret="test-api-key")  # type: ignore[arg-type]  # nosec B106
        assert isinstance(auth.secret, type(auth.secret))
        assert auth.secret.get_secret_value() == "test-api-key"

    def test_convert_to_secret_with_secretstr(self) -> None:
        """Test that convert_to_secret accepts SecretStr directly."""
        from pydantic import SecretStr

        secret = SecretStr("existing-secret")
        auth = AuthHeader(secret=secret)
        assert auth.secret is secret

    def test_get_headers_returns_correct_format(self) -> None:
        """Test that get_headers returns header dict with prefix."""
        auth = AuthHeader(
            secret=SecretStr("test-key"), header="Authorization", prefix="Bearer "
        )
        headers = auth.get_headers()
        assert headers == {"Authorization": "Bearer test-key"}

    def test_get_headers_with_custom_header_and_prefix(self) -> None:
        """Test that get_headers works with custom header name and prefix."""
        auth = AuthHeader(
            secret=SecretStr("api-key-123"), header="x-api-key", prefix=""
        )
        headers = auth.get_headers()
        assert headers == {"x-api-key": "api-key-123"}


class TestAPIAlias:
    """Test APIKey alias for AuthHeader."""

    def test_apikey_is_alias_for_authheader(self) -> None:
        """Test that APIKey is an alias for AuthHeader."""
        assert APIKey is AuthHeader


class TestAuthRegistry:
    """Test authentication class registry."""

    def test_register_auth_stores_auth_class(self) -> None:
        """Test that register_auth stores authentication class in registry."""

        class CustomAuth(Authentication):
            def get_headers(self) -> dict[str, str]:
                return {"Custom-Header": "value"}

        register_auth("custom", CustomAuth)
        retrieved = get_auth_class("custom")
        assert retrieved is CustomAuth

    def test_get_auth_class_with_unknown_type_raises(self) -> None:
        """Test that get_auth_class raises ValueError for unknown auth type."""
        with pytest.raises(
            ValueError, match=r"Unknown auth type: nonexistent.*Available:"
        ):
            get_auth_class("nonexistent")


@pytest.fixture
def openai_auth() -> AuthHeader:
    return AuthHeader(secret=SecretStr("openai-key"))


@pytest.fixture
def anthropic_auth() -> AuthHeader:
    return AuthHeader(secret=SecretStr("anthropic-key"))


@pytest.fixture
def elevenlabs_auth() -> NoAuth:
    return NoAuth()


@pytest.fixture
def full_context(
    openai_auth: AuthHeader,
    anthropic_auth: AuthHeader,
    elevenlabs_auth: NoAuth,
) -> AuthenticationContext:
    return AuthenticationContext(
        entries={
            Provider.OPENAI: openai_auth,
            Provider.ANTHROPIC: anthropic_auth,
            Provider.ELEVENLABS: elevenlabs_auth,
        }
    )


class TestAuthenticationContext:
    """Test AuthenticationContext pydantic model."""

    def test_frozen_rejects_mutation(self, full_context: AuthenticationContext) -> None:
        with pytest.raises(ValidationError):
            full_context.entries = {}  # type: ignore[misc]


class TestAuthenticationScope:
    """Test authentication_scope context manager."""

    def test_outside_scope_resolves_none(self) -> None:
        assert resolve_authentication(Provider.OPENAI) is None

    def test_inside_scope_resolves_bound_auth(
        self, full_context: AuthenticationContext, openai_auth: AuthHeader
    ) -> None:
        with authentication_scope(full_context):
            assert resolve_authentication(Provider.OPENAI) is openai_auth

    def test_exit_restores_previous_state(
        self, full_context: AuthenticationContext, openai_auth: AuthHeader
    ) -> None:
        assert resolve_authentication(Provider.OPENAI) is None
        with authentication_scope(full_context):
            assert resolve_authentication(Provider.OPENAI) is openai_auth
        assert resolve_authentication(Provider.OPENAI) is None

    def test_nested_scopes_inner_wins_outer_restored(
        self,
        full_context: AuthenticationContext,
        openai_auth: AuthHeader,
    ) -> None:
        inner_auth = AuthHeader(secret=SecretStr("inner-key"))
        inner_context = AuthenticationContext(entries={Provider.OPENAI: inner_auth})

        with authentication_scope(full_context):
            assert resolve_authentication(Provider.OPENAI) is openai_auth
            with authentication_scope(inner_context):
                assert resolve_authentication(Provider.OPENAI) is inner_auth
            assert resolve_authentication(Provider.OPENAI) is openai_auth

    def test_scope_with_none_clears_binding(
        self, full_context: AuthenticationContext, openai_auth: AuthHeader
    ) -> None:
        with authentication_scope(full_context):
            assert resolve_authentication(Provider.OPENAI) is openai_auth
            with authentication_scope(None):
                assert resolve_authentication(Provider.OPENAI) is None
            assert resolve_authentication(Provider.OPENAI) is openai_auth


class TestResolveAuthentication:
    """Test resolve_authentication lookup helper."""

    def test_scope_bound_but_provider_missing_raises(
        self, full_context: AuthenticationContext
    ) -> None:
        with (
            authentication_scope(full_context),
            pytest.raises(MissingAuthenticationError) as exc_info,
        ):
            resolve_authentication(Provider.GOOGLE)
        err = exc_info.value
        assert err.provider is Provider.GOOGLE
        assert "google" in str(err)


class TestAsyncPropagation:
    """Test ContextVar propagation across async boundaries."""

    @pytest.mark.asyncio
    async def test_create_task_propagates(
        self, full_context: AuthenticationContext, anthropic_auth: AuthHeader
    ) -> None:
        async def child() -> object:
            return resolve_authentication(Provider.ANTHROPIC)

        with authentication_scope(full_context):
            task = asyncio.create_task(child())
            result = await task

        assert result is anthropic_auth

    @pytest.mark.asyncio
    async def test_gather_siblings_share_snapshot(
        self, full_context: AuthenticationContext, anthropic_auth: AuthHeader
    ) -> None:
        async def child() -> object:
            return resolve_authentication(Provider.ANTHROPIC)

        with authentication_scope(full_context):
            results = await asyncio.gather(child(), child(), child())

        assert all(r is anthropic_auth for r in results)

    @pytest.mark.asyncio
    async def test_to_thread_propagates(
        self, full_context: AuthenticationContext, openai_auth: AuthHeader
    ) -> None:
        def sync_worker() -> object:
            return resolve_authentication(Provider.OPENAI)

        with authentication_scope(full_context):
            result = await asyncio.to_thread(sync_worker)

        assert result is openai_auth

    def test_raw_thread_pool_does_not_propagate(
        self, full_context: AuthenticationContext
    ) -> None:
        def sync_worker() -> object:
            return resolve_authentication(Provider.OPENAI)

        with (
            ThreadPoolExecutor(max_workers=1) as pool,
            authentication_scope(full_context),
        ):
            future = pool.submit(sync_worker)
            result = future.result()

        assert result is None

    def test_raw_thread_pool_with_copy_context_propagates(
        self, full_context: AuthenticationContext, openai_auth: AuthHeader
    ) -> None:
        def sync_worker() -> object:
            return resolve_authentication(Provider.OPENAI)

        with (
            ThreadPoolExecutor(max_workers=1) as pool,
            authentication_scope(full_context),
        ):
            ctx_snapshot = contextvars.copy_context()
            future = pool.submit(ctx_snapshot.run, sync_worker)
            result = future.result()

        assert result is openai_auth
