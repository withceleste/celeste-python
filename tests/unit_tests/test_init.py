"""Tests for public exports and client/model resolution."""

from unittest.mock import Mock, patch

import pytest

import celeste
from celeste import Modality, Model, Operation, Protocol, Provider, create_client
from celeste.auth import NoAuth
from celeste.exceptions import ClientNotFoundError, ModelNotFoundError


@pytest.fixture
def text_model() -> Model:
    return Model(
        id="text-model",
        provider=Provider.OPENAI,
        display_name="Text Model",
        operations={Modality.TEXT: {Operation.GENERATE}},
    )


def test_resolve_model_auto_selects_with_requested_filters(text_model: Model) -> None:
    with patch("celeste.list_models", return_value=[text_model]) as list_models:
        assert (
            celeste._resolve_model(
                modality=Modality.TEXT,
                operation=Operation.GENERATE,
                provider=Provider.OPENAI,
            )
            is text_model
        )
    list_models.assert_called_once_with(
        provider=Provider.OPENAI,
        modality=Modality.TEXT,
        operation=Operation.GENERATE,
    )


def test_resolve_model_reports_empty_selection() -> None:
    with (
        patch("celeste.list_models", return_value=[]),
        pytest.raises(
            ModelNotFoundError,
            match="No model found for modality 'text' with provider openai",
        ),
    ):
        celeste._resolve_model(modality=Modality.TEXT, provider=Provider.OPENAI)


def test_resolve_model_preserves_unregistered_provider_models() -> None:
    with (
        patch("celeste.get_model", return_value=None),
        pytest.warns(UserWarning, match="Parameter validation disabled"),
    ):
        resolved = celeste._resolve_model(
            modality=Modality.TEXT,
            operation=Operation.GENERATE,
            provider=Provider.HUGGINGFACE,
            model="org/unregistered-model",
        )

    assert resolved.provider is Provider.HUGGINGFACE
    assert resolved.operations == {Modality.TEXT: {Operation.GENERATE}}
    assert resolved.parameter_constraints == {}
    assert resolved.streaming is True


def test_resolve_model_allows_unregistered_protocol_models() -> None:
    with patch("celeste.get_model", return_value=None):
        resolved = celeste._resolve_model(
            modality=Modality.TEXT,
            operation=Operation.GENERATE,
            protocol=Protocol.OPENRESPONSES,
            model="remote-model",
        )

    assert resolved.provider is None
    assert resolved.streaming is True


@pytest.mark.parametrize(
    ("kwargs", "error", "message"),
    [
        ({}, ValueError, "Either 'modality' or 'model' must be provided"),
        (
            {"model": "unknown"},
            ModelNotFoundError,
            "Model 'unknown' not found",
        ),
        (
            {"model": "unknown", "provider": Provider.OPENAI},
            ValueError,
            "Specify 'modality' explicitly",
        ),
    ],
)
def test_resolve_model_rejects_insufficient_context(
    kwargs: dict[str, object], error: type[Exception], message: str
) -> None:
    with (
        patch("celeste.get_model", return_value=None),
        pytest.raises(error, match=message),
    ):
        celeste._resolve_model(**kwargs)  # type: ignore[arg-type]


def test_create_client_resolves_provider_client(text_model: Model) -> None:
    auth = NoAuth()
    client_class = Mock(return_value=Mock())
    with (
        patch("celeste.get_model", return_value=text_model),
        patch.dict(
            celeste._CLIENT_MAP,
            {(Modality.TEXT, Provider.OPENAI): client_class},
            clear=True,
        ),
    ):
        client = create_client(
            modality=Modality.TEXT,
            operation=Operation.GENERATE,
            provider=Provider.OPENAI,
            model=text_model.id,
            auth=auth,
        )

    assert client is client_class.return_value
    client_class.assert_called_once_with(
        modality=Modality.TEXT,
        model=text_model,
        provider=Provider.OPENAI,
        protocol=None,
        auth=auth,
        base_url=None,
    )


def test_create_client_reports_missing_route(text_model: Model) -> None:
    with (
        patch("celeste.get_model", return_value=text_model),
        patch.dict(celeste._CLIENT_MAP, {}, clear=True),
        pytest.raises(
            ClientNotFoundError,
            match="No client registered for modality 'text' with provider openai",
        ),
    ):
        create_client(modality=Modality.TEXT, model=text_model.id)
