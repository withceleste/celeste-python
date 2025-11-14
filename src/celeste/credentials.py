"""Provider API credentials management for Celeste."""

from dotenv import find_dotenv
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

from celeste.core import Provider
from celeste.exceptions import MissingCredentialsError, UnsupportedProviderError

# Provider to credential field mapping
PROVIDER_CREDENTIAL_MAP = {
    Provider.OPENAI: "openai_api_key",
    Provider.ANTHROPIC: "anthropic_api_key",
    Provider.GOOGLE: "google_api_key",
    Provider.MISTRAL: "mistral_api_key",
    Provider.HUGGINGFACE: "huggingface_token",
    Provider.STABILITYAI: "stabilityai_api_key",
    Provider.REPLICATE: "replicate_api_token",
    Provider.COHERE: "cohere_api_key",
    Provider.XAI: "xai_api_key",
    Provider.LUMA: "luma_api_key",
    Provider.TOPAZLABS: "topazlabs_api_key",
    Provider.PERPLEXITY: "perplexity_api_key",
    Provider.BYTEDANCE: "bytedance_api_key",
    Provider.ELEVENLABS: "elevenlabs_api_key",
}


class Credentials(BaseSettings):
    """API credentials for all supported providers."""

    openai_api_key: SecretStr | None = Field(None, alias="OPENAI_API_KEY")
    anthropic_api_key: SecretStr | None = Field(None, alias="ANTHROPIC_API_KEY")
    google_api_key: SecretStr | None = Field(None, alias="GOOGLE_API_KEY")
    mistral_api_key: SecretStr | None = Field(None, alias="MISTRAL_API_KEY")
    huggingface_token: SecretStr | None = Field(None, alias="HUGGINGFACE_TOKEN")
    stabilityai_api_key: SecretStr | None = Field(None, alias="STABILITYAI_API_KEY")
    replicate_api_token: SecretStr | None = Field(None, alias="REPLICATE_API_TOKEN")
    cohere_api_key: SecretStr | None = Field(None, alias="COHERE_API_KEY")
    xai_api_key: SecretStr | None = Field(None, alias="XAI_API_KEY")
    luma_api_key: SecretStr | None = Field(None, alias="LUMA_API_KEY")
    topazlabs_api_key: SecretStr | None = Field(None, alias="TOPAZLABS_API_KEY")
    perplexity_api_key: SecretStr | None = Field(None, alias="PERPLEXITY_API_KEY")
    bytedance_api_key: SecretStr | None = Field(None, alias="BYTEDANCE_API_KEY")
    elevenlabs_api_key: SecretStr | None = Field(None, alias="ELEVENLABS_API_KEY")

    model_config = {
        "env_file": find_dotenv(),
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",  # Ignore unknown env vars like context7_api_key
    }

    def get_credentials(
        self, provider: Provider, override_key: SecretStr | None = None
    ) -> SecretStr:
        """Get credentials for a specific provider with optional override.

        Args:
            provider: The AI provider to get credentials for.
            override_key: Optional SecretStr to use instead of environment variable.

        Returns:
            SecretStr containing the API key for the provider.

        Raises:
            MissingCredentialsError: If provider requires credentials but none are configured.
        """
        if override_key:
            return override_key

        if not self.has_credential(provider):
            raise MissingCredentialsError(provider=provider)

        credential: SecretStr = getattr(self, PROVIDER_CREDENTIAL_MAP[provider])
        return credential

    def list_available_providers(self) -> list[Provider]:
        """List all providers that have credentials configured.

        Returns:
            List of Provider enums that have credentials configured via environment variables.
        """
        return [
            provider
            for provider in PROVIDER_CREDENTIAL_MAP
            if self.has_credential(provider)
        ]

    def has_credential(self, provider: Provider) -> bool:
        """Check if a specific provider has credentials configured.

        Args:
            provider: The AI provider to check.

        Returns:
            True if provider has credentials configured, False if credentials not set.

        Raises:
            UnsupportedProviderError: If provider has no credential mapping.
        """
        credential_field = PROVIDER_CREDENTIAL_MAP.get(provider)
        if not credential_field:
            raise UnsupportedProviderError(provider=provider)
        return getattr(self, credential_field, None) is not None


credentials = Credentials.model_validate({})

__all__ = ["Credentials", "credentials"]
