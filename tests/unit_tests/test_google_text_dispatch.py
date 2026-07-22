"""Google text dispatcher: auth and model-id backend selection."""

from __future__ import annotations

import pytest
from pydantic import SecretStr

from celeste.auth import AuthHeader
from celeste.core import Modality, Provider
from celeste.modalities.text.providers.google.client import GoogleTextClient
from celeste.modalities.text.providers.google.interactions import (
    GoogleInteractionsTextClient,
)
from celeste.modalities.text.providers.google.vertex import GoogleVertexTextClient
from celeste.models import Model
from celeste.providers.google.auth import GoogleADC


def _client(model_id: str, *, adc: bool = False) -> GoogleTextClient:
    auth = (
        GoogleADC(project_id="p")
        if adc
        else AuthHeader(secret=SecretStr("test"), header="x-goog-api-key", prefix="")
    )
    return GoogleTextClient(
        modality=Modality.TEXT,
        model=Model(id=model_id, provider=Provider.GOOGLE, display_name=model_id),
        provider=Provider.GOOGLE,
        auth=auth,
    )


@pytest.mark.parametrize(
    ("model_id", "adc", "backend"),
    [
        ("gemini-3.5-flash", False, GoogleInteractionsTextClient),
        ("gemini-3.1-flash-lite", False, GoogleInteractionsTextClient),
        ("gemini-3.5-flash-lite", False, GoogleVertexTextClient),
        ("gemini-3.6-flash", False, GoogleVertexTextClient),
        ("gemini-3.5-flash-lite", True, GoogleVertexTextClient),
        ("gemini-3.6-flash", True, GoogleVertexTextClient),
        ("gemini-3.5-flash", True, GoogleVertexTextClient),
    ],
)
def test_google_text_dispatch(model_id: str, adc: bool, backend: type[object]) -> None:
    assert isinstance(_client(model_id, adc=adc)._strategy, backend)
