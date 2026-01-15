"""Tests for authentication classes and registry."""

from collections.abc import Generator

import pytest
from pydantic import SecretStr

from celeste.auth import (
    APIKey,
    Authentication,
    AuthHeader,
    get_auth_class,
    register_auth,
)


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
