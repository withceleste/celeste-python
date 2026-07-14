"""Tests for authentication primitives."""

import pytest
from pydantic import SecretStr

from celeste.auth import AuthHeader


@pytest.mark.parametrize("secret", [" key ", SecretStr(" key ")])
def test_auth_header_formats_and_strips_secret(secret: str | SecretStr) -> None:
    auth = AuthHeader(secret=secret, header="x-api-key", prefix="Token ")  # type: ignore[arg-type]
    assert auth.get_headers() == {"x-api-key": "Token key"}
