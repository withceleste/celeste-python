"""Unit tests for credentials.py following 2025 best practices."""

import os
from collections.abc import Generator
from unittest.mock import patch

import pytest
from pydantic import SecretStr

from celeste.core import Provider
from celeste.credentials import PROVIDER_CREDENTIAL_MAP, Credentials

# Single source of truth for environment variable names
ENV_VAR_NAMES = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY",
    "MISTRAL_API_KEY",
    "HUGGINGFACE_TOKEN",
    "STABILITYAI_API_KEY",
    "REPLICATE_API_TOKEN",
    "COHERE_API_KEY",
    "XAI_API_KEY",
    "LUMA_API_KEY",
    "TOPAZLABS_API_KEY",
]


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    """Clear all environment variables before each test to ensure isolation.

    This prevents tests from failing when .env files load API keys into the
    environment. Uses a two-part approach:

    1. monkeypatch.setattr: Disables pydantic-settings .env file loading by
       setting env_file=None. This prevents Credentials from reading .env
       during initialization.

    2. patch.dict(os.environ, clear=True): Clears all existing environment
       variables so tests start with a clean slate. Required because .env
       files may have already loaded vars into os.environ before test execution.

    Both are necessary: monkeypatch prevents future .env reads, patch.dict
    clears existing state.
    """
    # Disable .env file loading for Credentials class during tests
    monkeypatch.setattr(
        Credentials,
        "model_config",
        {
            "env_file": None,
            "env_file_encoding": "utf-8",
            "case_sensitive": False,
            "extra": "ignore",
        },
    )

    # Clear all environment variables
    with patch.dict(os.environ, clear=True):
        yield


class TestCredentialsLoading:
    """Test loading credentials from environment."""

    @pytest.mark.smoke
    def test_load_from_env_single_provider(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test loading a single provider credential from environment."""
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        # Act
        creds = Credentials()  # type: ignore[call-arg]

        # Assert
        assert creds.openai_api_key is not None
        assert creds.openai_api_key.get_secret_value() == "test-key"

    def test_load_multiple_providers(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test loading multiple provider credentials."""
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "anthropic-key")

        # Act
        creds = Credentials()  # type: ignore[call-arg]

        # Assert
        assert creds.openai_api_key is not None
        assert creds.anthropic_api_key is not None
        assert creds.openai_api_key.get_secret_value() == "openai-key"
        assert creds.anthropic_api_key.get_secret_value() == "anthropic-key"
        assert creds.google_api_key is None

    def test_empty_credentials(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test when no credentials are set."""
        # Arrange - clear any existing env vars
        for env_var in ENV_VAR_NAMES:
            monkeypatch.delenv(env_var, raising=False)

        # Act
        creds = Credentials()  # type: ignore[call-arg]

        # Assert - verify ALL credential fields are None
        for _provider, field_name in PROVIDER_CREDENTIAL_MAP.items():
            assert getattr(creds, field_name) is None, (
                f"{field_name} should be None when no env vars set"
            )


class TestGetCredentials:
    """Test get_credentials method following AAA pattern."""

    @pytest.mark.smoke
    def test_get_existing_credential(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test retrieving an existing credential."""
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        creds = Credentials()  # type: ignore[call-arg]

        # Act
        result = creds.get_credentials(Provider.OPENAI)

        # Assert
        assert isinstance(result, SecretStr)
        assert result.get_secret_value() == "test-key"

    def test_get_missing_credential_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that missing credentials raise ValueError."""
        # Arrange
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        creds = Credentials()  # type: ignore[call-arg]

        # Act & Assert
        with pytest.raises(ValueError, match="no credentials configured"):
            creds.get_credentials(Provider.OPENAI)

    @pytest.mark.parametrize(
        "provider,env_var,value",
        [
            (Provider.OPENAI, "OPENAI_API_KEY", "openai-test"),
            (Provider.ANTHROPIC, "ANTHROPIC_API_KEY", "anthropic-test"),
            (Provider.GOOGLE, "GOOGLE_API_KEY", "google-test"),
            (Provider.MISTRAL, "MISTRAL_API_KEY", "mistral-test"),
        ],
    )
    def test_get_credentials_parametrized(
        self,
        monkeypatch: pytest.MonkeyPatch,
        provider: Provider,
        env_var: str,
        value: str,
    ) -> None:
        """Test get_credentials for various providers."""
        # Arrange
        monkeypatch.setenv(env_var, value)
        creds = Credentials()  # type: ignore[call-arg]

        # Act
        result = creds.get_credentials(provider)

        # Assert
        assert result.get_secret_value() == value


class TestHasCredential:
    """Test has_credential method."""

    @pytest.mark.parametrize(
        "provider,env_var",
        [
            (Provider.OPENAI, "OPENAI_API_KEY"),
            (Provider.GOOGLE, "GOOGLE_API_KEY"),
            (Provider.ANTHROPIC, "ANTHROPIC_API_KEY"),
        ],
    )
    def test_has_credential_when_set(
        self, monkeypatch: pytest.MonkeyPatch, provider: Provider, env_var: str
    ) -> None:
        """Test has_credential returns True when credential exists."""
        # Arrange
        monkeypatch.setenv(env_var, "test-value")
        creds = Credentials()  # type: ignore[call-arg]

        # Act
        result = creds.has_credential(provider)

        # Assert
        assert result is True

    def test_has_credential_when_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test has_credential returns False when missing."""
        # Arrange
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        creds = Credentials()  # type: ignore[call-arg]

        # Act & Assert
        assert creds.has_credential(Provider.OPENAI) is False


class TestListAvailableProviders:
    """Test list_available_providers method."""

    @pytest.mark.smoke
    def test_list_with_mixed_providers(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test listing returns only providers with credentials."""
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "test1")
        monkeypatch.setenv("GOOGLE_API_KEY", "test2")
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        creds = Credentials()  # type: ignore[call-arg]

        # Act
        providers = creds.list_available_providers()

        # Assert
        assert Provider.OPENAI in providers
        assert Provider.GOOGLE in providers
        assert Provider.ANTHROPIC not in providers
        assert len(providers) == 2

    def test_empty_list_when_no_credentials(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test empty list when no credentials configured."""
        # Arrange - clear all credential env vars
        for env_var in ENV_VAR_NAMES:
            monkeypatch.delenv(env_var, raising=False)
        creds = Credentials()  # type: ignore[call-arg]

        # Act
        result = creds.list_available_providers()

        # Assert
        assert result == []


class TestCredentialSecurity:
    """Test security features of credentials."""

    @pytest.mark.smoke
    def test_secret_str_hides_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test SecretStr doesn't expose values in string representation."""
        # Arrange
        secret_value = "super-secret-api-key"  # nosec B105
        monkeypatch.setenv("OPENAI_API_KEY", secret_value)
        creds = Credentials()  # type: ignore[call-arg]

        # Act
        credential = creds.get_credentials(Provider.OPENAI)

        # Assert
        assert secret_value not in str(credential)
        assert secret_value not in repr(credential)
        assert credential.get_secret_value() == secret_value

    def test_model_dump_masks_secrets(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test model_dump masks secret values."""
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", "secret-key")
        creds = Credentials()  # type: ignore[call-arg]

        # Act
        dumped = creds.model_dump()

        # Assert
        assert isinstance(dumped["openai_api_key"], SecretStr)
        assert str(dumped["openai_api_key"]) == "**********"
        assert "secret-key" not in str(dumped)

    def test_credentials_safe_for_logging(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test that credentials object is safe to log without exposing secrets.

        This test prevents a critical security issue where developers might
        accidentally log the entire credentials object, potentially exposing
        API keys in production logs.
        """
        import logging

        # Arrange
        secret_value = "secret-key-12345"  # nosec B105
        monkeypatch.setenv("OPENAI_API_KEY", secret_value)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "another-secret-xyz")
        creds = Credentials()  # type: ignore[call-arg]

        # Act - simulate common logging scenarios
        logger = logging.getLogger(__name__)
        caplog.set_level(logging.DEBUG)

        logger.info(f"Credentials initialized: {creds}")
        logger.debug(f"Debug credentials repr: {creds!r}")
        logger.error(f"Error with credentials: {creds!s}")

        # Assert - ensure no secrets appear in any log level
        assert secret_value not in caplog.text
        assert "another-secret-xyz" not in caplog.text
        # Verify that some form of masking is present
        assert "**********" in caplog.text or "SecretStr" in caplog.text


class TestProviderMapping:
    """Test integrity of provider-credential mapping."""

    def test_all_mapped_fields_exist(self) -> None:
        """Test all fields in mapping exist on Credentials class."""
        # Arrange
        creds = Credentials()  # type: ignore[call-arg]

        # Act & Assert - verify each mapping points to a real field
        for provider, field_name in PROVIDER_CREDENTIAL_MAP.items():
            assert hasattr(creds, field_name), (
                f"Missing field {field_name} for {provider}"
            )

    def test_all_providers_have_credential_mapping(self) -> None:
        """Every Provider enum value has a corresponding entry in PROVIDER_CREDENTIAL_MAP."""
        # Get all providers that should have credentials
        # Note: All providers in Provider enum require credentials
        all_providers = list(Provider)

        # Verify each provider has a mapping
        for provider in all_providers:
            assert provider in PROVIDER_CREDENTIAL_MAP, (
                f"Provider {provider.value} missing from PROVIDER_CREDENTIAL_MAP"
            )


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.parametrize("value", ["", "   ", "\t\n"])
    def test_whitespace_credentials(
        self, monkeypatch: pytest.MonkeyPatch, value: str
    ) -> None:
        """Test handling of whitespace-only credentials.

        Note: Currently treats whitespace as 'present' credentials.
        This is a deliberate choice - empty/whitespace values are still
        considered as having credentials set (may be used for optional APIs).
        """
        # Arrange
        monkeypatch.setenv("OPENAI_API_KEY", value)
        creds = Credentials()  # type: ignore[call-arg]

        # Act & Assert
        assert creds.has_credential(Provider.OPENAI) is True
        credential = creds.get_credentials(Provider.OPENAI)
        assert credential.get_secret_value() == value

    def test_special_characters_in_credentials(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test handling of special characters in API keys."""
        # Arrange
        special_key = "test!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
        monkeypatch.setenv("OPENAI_API_KEY", special_key)
        creds = Credentials()  # type: ignore[call-arg]

        # Act
        credential = creds.get_credentials(Provider.OPENAI)

        # Assert
        assert credential.get_secret_value() == special_key
