"""Tests for model registration, lookup, and filtering."""

from typing import Any

import pytest

import celeste.models as models_module
from celeste import Modality, Model, Operation, Provider
from celeste.constraints import Str
from celeste.models import get_model, list_models, register_models


def model(
    model_id: str,
    provider: Provider | None = Provider.OPENAI,
    *,
    modality: Modality | None = None,
    operation: Operation = Operation.GENERATE,
) -> Model:
    operations = {modality: {operation}} if modality else {}
    return Model(
        id=model_id,
        provider=provider,
        display_name=model_id,
        operations=operations,
    )


@pytest.fixture(autouse=True)
def isolated_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(models_module, "_models", {})


@pytest.mark.parametrize(
    ("models", "expected"),
    [
        (model("one"), {"one"}),
        ([model("one"), model("two", Provider.ANTHROPIC)], {"one", "two"}),
    ],
)
def test_register_models_accepts_one_or_many(
    models: Model | list[Model], expected: set[str]
) -> None:
    register_models(models)
    assert {registered.id for registered in list_models()} == expected


def test_register_models_requires_provider() -> None:
    with pytest.raises(ValueError, match="without a provider"):
        register_models(model("local", None))


def test_reregistration_merges_contracts_and_rejects_rename() -> None:
    original = model("shared", modality=Modality.TEXT)
    original.parameter_constraints = {"temperature": Str()}
    register_models(original)

    extension = model("shared", modality=Modality.IMAGES, operation=Operation.EDIT)
    extension.parameter_constraints = {"seed": Str()}
    register_models(extension, modality=Modality.EMBEDDINGS, operation=Operation.EMBED)

    registered = get_model("shared", Provider.OPENAI)
    assert registered is not None
    assert registered.operations == {
        Modality.TEXT: {Operation.GENERATE},
        Modality.IMAGES: {Operation.EDIT},
        Modality.EMBEDDINGS: {Operation.EMBED},
    }
    assert registered.supported_parameters == {"temperature", "seed"}

    renamed = extension.model_copy(update={"display_name": "renamed"})
    with pytest.raises(ValueError, match="Inconsistent display_name"):
        register_models(renamed)


@pytest.fixture
def populated_registry() -> None:
    register_models(
        [
            model("text-openai", modality=Modality.TEXT),
            model("image-openai", modality=Modality.IMAGES),
            model(
                "text-anthropic",
                Provider.ANTHROPIC,
                modality=Modality.TEXT,
                operation=Operation.ANALYZE,
            ),
        ]
    )


@pytest.mark.parametrize(
    ("filters", "expected"),
    [
        ({}, {"text-openai", "image-openai", "text-anthropic"}),
        ({"provider": Provider.OPENAI}, {"text-openai", "image-openai"}),
        ({"modality": Modality.TEXT}, {"text-openai", "text-anthropic"}),
        ({"operation": Operation.GENERATE}, {"text-openai", "image-openai"}),
        (
            {"modality": Modality.TEXT, "operation": Operation.GENERATE},
            {"text-openai"},
        ),
        (
            {"provider": Provider.GOOGLE, "modality": Modality.TEXT},
            set(),
        ),
    ],
)
def test_list_models_filters(
    populated_registry: None, filters: dict[str, Any], expected: set[str]
) -> None:
    assert {registered.id for registered in list_models(**filters)} == expected


def test_get_model_distinguishes_providers_and_warns_when_ambiguous() -> None:
    register_models([model("shared"), model("shared", Provider.ANTHROPIC)])

    assert get_model("shared", Provider.ANTHROPIC).provider is Provider.ANTHROPIC  # type: ignore[union-attr]
    assert get_model("missing", Provider.OPENAI) is None
    with pytest.warns(UserWarning, match="found in multiple providers"):
        assert get_model("shared").provider is Provider.OPENAI  # type: ignore[union-attr]
