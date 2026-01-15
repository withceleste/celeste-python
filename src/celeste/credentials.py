"""Provider API credentials management for Celeste."""

from dotenv import find_dotenv
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

from celeste.auth import (
    Authentication,
    AuthHeader,
)
from celeste.core import Provider
from celeste.exceptions import MissingCredentialsError, UnsupportedProviderError

# Auth registry - populated by provider packages via register_auth()
# Maps provider to either:
# - tuple[str, str, str] for API key auth (secret_name, header, prefix)
# - type[Authentication] for custom auth classes (GoogleADC, OAuth, etc.)
_auth_registry: dict[Provider, tuple[str, str, str] | type[Authentication]] = {}


def register_auth(
    provider: Provider,
    *,
    secret_name: str | None = None,
    header: str | None = None,
    prefix: str | None = None,
    auth_class: type[Authentication] | None = None,
) -> None:
    """Register auth for a provider."""
    if auth_class is not None:
        _auth_registry[provider] = auth_class
    elif secret_name is not None and header is not None and prefix is not None:
        _auth_registry[provider] = (secret_name, header, prefix)
    else:
        msg = "Provide auth_class OR (secret_name, header, prefix)"
        raise ValueError(msg)


def get_auth_config(
    provider: Provider,
) -> tuple[str, str, str] | type[Authentication]:
    """Get registered auth config for a provider.

    Returns:
        Tuple of (secret_name, header, prefix) or an Authentication class.

    Raises:
        UnsupportedProviderError: If provider has no registered auth config.
    """
    if provider in _auth_registry:
        return _auth_registry[provider]

    raise UnsupportedProviderError(provider=provider)


class Credentials(BaseSettings):
    """API credentials for all supported providers."""

    openai_api_key: SecretStr | None = Field(None, alias="OPENAI_API_KEY")
    anthropic_api_key: SecretStr | None = Field(None, alias="ANTHROPIC_API_KEY")
    google_api_key: SecretStr | None = Field(None, alias="GOOGLE_API_KEY")
    mistral_api_key: SecretStr | None = Field(None, alias="MISTRAL_API_KEY")
    moonshot_api_key: SecretStr | None = Field(None, alias="MOONSHOT_API_KEY")
    huggingface_token: SecretStr | None = Field(None, alias="HUGGINGFACE_TOKEN")
    stabilityai_api_key: SecretStr | None = Field(None, alias="STABILITYAI_API_KEY")
    replicate_api_token: SecretStr | None = Field(None, alias="REPLICATE_API_TOKEN")
    cohere_api_key: SecretStr | None = Field(None, alias="COHERE_API_KEY")
    xai_api_key: SecretStr | None = Field(None, alias="XAI_API_KEY")
    deepseek_api_key: SecretStr | None = Field(None, alias="DEEPSEEK_API_KEY")
    luma_api_key: SecretStr | None = Field(None, alias="LUMA_API_KEY")
    topazlabs_api_key: SecretStr | None = Field(None, alias="TOPAZLABS_API_KEY")
    perplexity_api_key: SecretStr | None = Field(None, alias="PERPLEXITY_API_KEY")
    byteplus_api_key: SecretStr | None = Field(None, alias="BYTEPLUS_API_KEY")
    elevenlabs_api_key: SecretStr | None = Field(None, alias="ELEVENLABS_API_KEY")
    bfl_api_key: SecretStr | None = Field(None, alias="BFL_API_KEY")
    groq_api_key: SecretStr | None = Field(None, alias="GROQ_API_KEY")
    gradium_api_key: SecretStr | None = Field(None, alias="GRADIUM_API_KEY")

    model_config = {
        "env_file": find_dotenv(),
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",  # Ignore unknown env vars like context7_api_key
    }

    def get_credentials(
        self, provider: Provider, override_key: str | SecretStr | None = None
    ) -> SecretStr:
        """Get credentials for a specific provider with optional override.

        Args:
            provider: The AI provider to get credentials for.
            override_key: Optional key to use instead of environment variable.

        Returns:
            SecretStr containing the API key for the provider.

        Raises:
            MissingCredentialsError: If provider requires credentials but none are configured.
        """
        if override_key:
            if isinstance(override_key, str):
                return SecretStr(override_key)
            return override_key

        registered = _auth_registry.get(provider)
        if registered is None:
            raise UnsupportedProviderError(provider=provider)

        # Auth class doesn't use API keys
        if isinstance(registered, type):
            msg = f"{provider} uses auth class, not API key"
            raise ValueError(msg)

        secret_name, _, _ = registered
        field_name = secret_name.lower()

        credential: SecretStr | None = getattr(self, field_name, None)
        if credential is None:
            raise MissingCredentialsError(provider=provider)

        return credential

    def list_available_providers(self) -> list[Provider]:
        """List all providers that have credentials configured."""
        return [
            provider
            for provider in Provider
            if provider in _auth_registry and self.has_credential(provider)
        ]

    def has_credential(self, provider: Provider) -> bool:
        """Check if a specific provider has credentials configured."""
        registered = _auth_registry.get(provider)
        if registered is None:
            raise UnsupportedProviderError(provider=provider)

        # Auth class is always "configured" (uses ADC/OAuth)
        if isinstance(registered, type):
            return True

        secret_name, _, _ = registered
        field_name = secret_name.lower()

        return getattr(self, field_name, None) is not None

    def get_auth(
        self,
        provider: Provider,
        override_auth: Authentication | None = None,
        override_key: str | SecretStr | None = None,
    ) -> Authentication:
        """Get authentication for a specific provider.

        Args:
            provider: The AI provider to authenticate with.
            override_auth: Optional Authentication object to use directly.
            override_key: Optional API key to use instead of environment variable.

        Returns:
            Authentication object configured for the provider.

        Raises:
            MissingCredentialsError: If provider requires credentials but none configured.
            UnsupportedProviderError: If provider has no auth configuration.
        """
        if override_auth is not None:
            return override_auth

        registered = _auth_registry.get(provider)
        if registered is None:
            raise UnsupportedProviderError(provider=provider)

        # Auth class (GoogleADC, OAuth, etc.) → instantiate
        if isinstance(registered, type):
            return registered()

        # API key config tuple → AuthHeader
        _secret_name, header, prefix = registered
        api_key = self.get_credentials(provider, override_key)
        return AuthHeader(secret=api_key, header=header, prefix=prefix)


credentials = Credentials.model_validate({})

__all__ = [
    "Credentials",
    "credentials",
    "get_auth_config",
    "register_auth",
]
