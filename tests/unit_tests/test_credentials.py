import importlib
from collections.abc import Generator

import pytest
from pydantic import SecretStr

from celeste.auth import AuthHeader
from celeste.core import Provider
from celeste.credentials import Credentials, get_auth_config, register_auth
from celeste.exceptions import MissingCredentialsError, UnsupportedProviderError

credentials_module = importlib.import_module("celeste.credentials")


PROVIDERS = [
    (Provider.OPENAI, "OPENAI_API_KEY", "Authorization", "Bearer "),
    (Provider.ANTHROPIC, "ANTHROPIC_API_KEY", "x-api-key", ""),
    (Provider.GOOGLE, "GOOGLE_API_KEY", "x-goog-api-key", ""),
    (Provider.MISTRAL, "MISTRAL_API_KEY", "Authorization", "Bearer "),
]


@pytest.fixture(autouse=True)
def isolated_credentials(monkeypatch: pytest.MonkeyPatch) -> Generator[None]:
    monkeypatch.setattr(
        Credentials,
        "model_config",
        {
            "env_file": None,
            "case_sensitive": False,
            "extra": "ignore",
        },
    )
    for field in Credentials.model_fields.values():
        if field.alias:
            monkeypatch.delenv(field.alias, raising=False)

    previous = credentials_module._auth_registry.copy()
    credentials_module._auth_registry.clear()
    for provider, secret, header, prefix in PROVIDERS:
        register_auth(
            provider,
            secret_name=secret,
            header=header,
            prefix=prefix,
        )
    yield
    credentials_module._auth_registry.clear()
    credentials_module._auth_registry.update(previous)


@pytest.mark.parametrize(("provider", "env_var", "_header", "_prefix"), PROVIDERS)
def test_credentials_load_and_resolve_registered_provider(
    monkeypatch: pytest.MonkeyPatch,
    provider: Provider,
    env_var: str,
    _header: str,
    _prefix: str,
) -> None:
    monkeypatch.setenv(env_var, "test-key")
    credentials = Credentials()

    assert credentials.get_credentials(provider).get_secret_value() == "test-key"
    assert credentials.has_credential(provider)
    assert credentials.list_available_providers() == [provider]


def test_auth_uses_registered_header_and_prefix(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    auth = Credentials().get_auth(Provider.ANTHROPIC)

    assert isinstance(auth, AuthHeader)
    assert auth.get_headers() == {"x-api-key": "test-key"}
    assert get_auth_config(Provider.ANTHROPIC) == (
        "ANTHROPIC_API_KEY",
        "x-api-key",
        "",
    )


@pytest.mark.parametrize("value", [None, "", "   ", "\t\n"])
def test_missing_or_blank_environment_credentials_fail(
    monkeypatch: pytest.MonkeyPatch, value: str | None
) -> None:
    if value is not None:
        monkeypatch.setenv("OPENAI_API_KEY", value)
    credentials = Credentials()

    assert not credentials.has_credential(Provider.OPENAI)
    with pytest.raises(MissingCredentialsError):
        credentials.get_credentials(Provider.OPENAI)


@pytest.mark.parametrize("value", ["", "   ", SecretStr(""), SecretStr("\t")])
def test_blank_override_never_falls_through_to_environment(
    monkeypatch: pytest.MonkeyPatch, value: str | SecretStr
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "environment-key")
    with pytest.raises(MissingCredentialsError):
        Credentials().get_credentials(Provider.OPENAI, override_key=value)


def test_valid_override_takes_precedence(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "environment-key")
    result = Credentials().get_credentials(
        Provider.OPENAI, override_key=SecretStr("override-key")
    )
    assert result.get_secret_value() == "override-key"


def test_secret_is_masked_by_credentials_representation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value = "never-log-this"
    monkeypatch.setenv("OPENAI_API_KEY", value)
    credentials = Credentials()

    assert value not in str(credentials)
    assert value not in repr(credentials)
    assert value not in str(credentials.model_dump())


def test_unregistered_provider_is_rejected() -> None:
    with pytest.raises(UnsupportedProviderError):
        Credentials().get_credentials(Provider.COHERE)
    with pytest.raises(UnsupportedProviderError):
        get_auth_config(Provider.COHERE)


def test_register_auth_requires_a_complete_configuration() -> None:
    with pytest.raises(ValueError, match="Provide auth_class OR"):
        register_auth(Provider.COHERE, header="x-api-key")
