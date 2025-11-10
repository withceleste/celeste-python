"""Tests for models and model registry."""

from collections.abc import Generator
from unittest.mock import MagicMock, Mock, patch

import pytest

from celeste import Capability, Model, Provider
from celeste.constraints import Str
from celeste.models import clear, get_model, list_models, register_models

# Test data constants
SAMPLE_MODELS = [
    Model(
        id="gpt-4",
        provider=Provider.OPENAI,
        display_name="GPT-4",
    ),
    Model(
        id="dall-e-3",
        provider=Provider.OPENAI,
        display_name="DALL-E 3",
    ),
    Model(
        id="claude-3",
        provider=Provider.ANTHROPIC,
        display_name="Claude 3",
    ),
]


@pytest.fixture(autouse=True)
def clear_registry() -> Generator[None, None, None]:
    """Clear registry before and after each test for isolation."""
    clear()
    yield
    clear()


class TestRegisterModels:
    """Test model registration functionality."""

    @pytest.mark.smoke
    @patch("celeste.registry._load_from_entry_points")
    def test_register_models_accepts_single_or_list(self, mock_load: Mock) -> None:
        """Registering models works with both single model and list."""
        # Prevent entry point loading from interfering with test isolation
        mock_load.return_value = None
        single_model = SAMPLE_MODELS[0]
        register_models(single_model, Capability.TEXT_GENERATION)
        retrieved = get_model(single_model.id, single_model.provider)
        assert retrieved is not None
        assert retrieved.id == single_model.id
        assert retrieved.provider == single_model.provider
        assert retrieved.display_name == single_model.display_name
        assert Capability.TEXT_GENERATION in retrieved.capabilities

        clear()

        register_models(SAMPLE_MODELS, Capability.TEXT_GENERATION)
        assert len(list_models()) == 3
        for model in SAMPLE_MODELS:
            retrieved = get_model(model.id, model.provider)
            assert retrieved is not None
            assert model.id == retrieved.id
            assert model.provider == retrieved.provider
            assert Capability.TEXT_GENERATION in retrieved.capabilities

    @patch("celeste.registry._load_from_entry_points")
    def test_reregistering_same_key_raises_error(self, mock_load: Mock) -> None:
        """Re-registering with same (id, provider) but different display_name raises ValueError."""
        # Prevent entry point loading from interfering with test isolation
        mock_load.return_value = None
        original = SAMPLE_MODELS[0]
        register_models(original, Capability.TEXT_GENERATION)

        duplicate = Model(
            id=original.id,
            provider=original.provider,
            display_name="Duplicate GPT-4",
        )

        with pytest.raises(ValueError, match="Inconsistent display_name"):
            register_models(duplicate, Capability.IMAGE_GENERATION)

        result = get_model(original.id, original.provider)
        assert result is not None
        assert result.display_name == original.display_name
        assert len(list_models()) == 1

    @patch("celeste.registry._load_from_entry_points")
    def test_registering_same_model_for_multiple_capabilities_merges(
        self, mock_load: Mock
    ) -> None:
        """Registering the same model for multiple capabilities merges capabilities."""
        # Prevent entry point loading from interfering with test isolation
        mock_load.return_value = None
        model = Model(
            id="multi-cap-model",
            provider=Provider.OPENAI,
            display_name="Multi-Cap Model",
        )

        register_models(model, Capability.TEXT_GENERATION)
        retrieved = get_model("multi-cap-model", Provider.OPENAI)
        assert retrieved is not None
        assert Capability.TEXT_GENERATION in retrieved.capabilities
        assert Capability.EMBEDDINGS not in retrieved.capabilities

        # Register same model for different capability
        embeddings_model = Model(
            id="multi-cap-model",
            provider=Provider.OPENAI,
            display_name="Multi-Cap Model",
        )
        register_models(embeddings_model, Capability.EMBEDDINGS)

        retrieved = get_model("multi-cap-model", Provider.OPENAI)
        assert retrieved is not None
        assert Capability.TEXT_GENERATION in retrieved.capabilities
        assert Capability.EMBEDDINGS in retrieved.capabilities
        assert len(list_models()) == 1


class TestListModels:
    """Test model listing and filtering functionality."""

    @pytest.fixture(autouse=True)
    def setup_models(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Set up test models for filtering tests."""
        # Prevent entry point loading from interfering with test isolation
        monkeypatch.setattr("celeste.registry._load_from_entry_points", lambda: None)
        register_models(SAMPLE_MODELS[0], Capability.TEXT_GENERATION)
        register_models(SAMPLE_MODELS[1], Capability.IMAGE_GENERATION)
        register_models(SAMPLE_MODELS[2], Capability.TEXT_GENERATION)

    def test_list_all_models(self) -> None:
        """Listing all models without filters."""
        models = list_models()
        assert len(models) == 3
        assert set(m.id for m in models) == {"gpt-4", "dall-e-3", "claude-3"}

    def test_filter_by_provider(self) -> None:
        """Filtering models by provider."""
        openai_models = list_models(provider=Provider.OPENAI)
        assert len(openai_models) == 2
        assert all(m.provider == Provider.OPENAI for m in openai_models)

        anthropic_models = list_models(provider=Provider.ANTHROPIC)
        assert len(anthropic_models) == 1
        assert anthropic_models[0].id == "claude-3"

    def test_filter_by_capability(self) -> None:
        """Filtering models by capability."""
        text_models = list_models(capability=Capability.TEXT_GENERATION)
        assert len(text_models) == 2
        assert all(Capability.TEXT_GENERATION in m.capabilities for m in text_models)

        image_models = list_models(capability=Capability.IMAGE_GENERATION)
        assert len(image_models) == 1
        assert image_models[0].id == "dall-e-3"

    def test_filter_by_both_provider_and_capability(self) -> None:
        """Filtering with multiple criteria."""
        models = list_models(
            provider=Provider.OPENAI,
            capability=Capability.TEXT_GENERATION,
        )
        assert len(models) == 1
        assert models[0].id == "gpt-4"

    @pytest.mark.parametrize(
        "provider,capability",
        [
            (Provider.GOOGLE, None),
            (Provider.ANTHROPIC, Capability.IMAGE_GENERATION),
        ],
        ids=["wrong_provider", "wrong_provider_and_capability"],
    )
    def test_filter_returns_empty_when_no_match(
        self, provider: Provider, capability: Capability | None
    ) -> None:
        """Filters return empty list when no models match."""
        assert list_models(provider=provider, capability=capability) == []


class TestGetModel:
    """Test individual model retrieval."""

    def test_get_existing_model(self) -> None:
        """Retrieving an existing model by id and provider."""
        model = SAMPLE_MODELS[0]
        register_models(model, Capability.TEXT_GENERATION)

        result = get_model(model.id, model.provider)
        assert result is not None
        assert result.id == model.id
        assert result.provider == model.provider

    def test_get_nonexistent_model_from_empty_registry_returns_none(self) -> None:
        """Getting a model from empty registry returns None."""
        assert get_model("nonexistent", Provider.OPENAI) is None

    @pytest.mark.parametrize(
        "model_id,provider",
        [("gpt-5", Provider.OPENAI), ("gpt-4", Provider.ANTHROPIC)],
        ids=["wrong_id", "wrong_provider"],
    )
    def test_get_model_from_populated_registry_with_wrong_key(
        self, model_id: str, provider: Provider
    ) -> None:
        """get_model returns None for non-existent model in populated registry."""
        register_models(SAMPLE_MODELS[0], Capability.TEXT_GENERATION)
        register_models(SAMPLE_MODELS[1], Capability.IMAGE_GENERATION)
        register_models(SAMPLE_MODELS[2], Capability.TEXT_GENERATION)
        assert get_model(model_id, provider) is None

    def test_same_id_different_providers_are_distinct(self) -> None:
        """Models with same ID but different providers are kept distinct."""
        model1 = Model(
            id="shared-id",
            provider=Provider.OPENAI,
            display_name="OpenAI Model",
        )
        model2 = Model(
            id="shared-id",
            provider=Provider.ANTHROPIC,
            display_name="Anthropic Model",
        )

        register_models([model1, model2], Capability.TEXT_GENERATION)

        retrieved1 = get_model("shared-id", Provider.OPENAI)
        retrieved2 = get_model("shared-id", Provider.ANTHROPIC)
        assert retrieved1 is not None
        assert retrieved1.id == model1.id
        assert retrieved1.provider == model1.provider
        assert retrieved1.display_name == model1.display_name
        assert retrieved2 is not None
        assert retrieved2.id == model2.id
        assert retrieved2.provider == model2.provider
        assert retrieved2.display_name == model2.display_name


class TestEntryPoints:
    """Test entry point loading functionality."""

    @patch("celeste.registry.importlib.metadata.entry_points")
    def test_entry_point_loading_success(
        self, mock_entry_points: Mock, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Successful loading of models from entry points."""
        mock_ep = MagicMock()
        mock_ep.name = "test_models"
        test_model = Model(
            id="ep-test-model",
            provider=Provider.OPENAI,
            display_name="Entry Point Test Model",
        )
        mock_ep.load.return_value = lambda: register_models(
            test_model, Capability.TEXT_GENERATION
        )

        mock_entry_points.return_value = [mock_ep]

        clear()
        from celeste.registry import _load_from_entry_points

        _load_from_entry_points()

        models = list_models()
        assert any(m.id == "ep-test-model" for m in models)

        captured = capsys.readouterr()
        assert captured.err == ""

    @patch("celeste.registry.importlib.metadata.entry_points")
    def test_entry_point_returns_none_handled(
        self, mock_entry_points: Mock, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Entry points returning None are handled gracefully."""
        mock_ep = MagicMock()
        mock_ep.name = "empty_models"
        mock_ep.load.return_value = lambda: None

        mock_entry_points.return_value = [mock_ep]

        clear()
        from celeste.registry import _load_from_entry_points

        _load_from_entry_points()

        captured = capsys.readouterr()
        assert captured.err == ""


class TestParameterSupport:
    """Test registry with models that have supported parameters."""

    def test_register_model_with_parameters(self) -> None:
        """Models with parameter_constraints are registered correctly."""
        model = Model(
            id="param-model",
            provider=Provider.OPENAI,
            display_name="Model with Params",
            parameter_constraints={"temperature": Str(), "max_tokens": Str()},
        )

        register_models(model, Capability.TEXT_GENERATION)
        retrieved = get_model("param-model", Provider.OPENAI)

        assert retrieved is not None
        assert len(retrieved.supported_parameters) == 2
        assert "temperature" in retrieved.supported_parameters
        assert "max_tokens" in retrieved.supported_parameters

    def test_list_models_includes_parameters(self) -> None:
        """list_models returns models with their parameter_constraints intact."""
        models = [
            Model(
                id="with-params",
                provider=Provider.ANTHROPIC,
                display_name="With Params",
                parameter_constraints={"feature_a": Str(), "feature_b": Str()},
            ),
            Model(
                id="without-params",
                provider=Provider.GOOGLE,
                display_name="Without Params",
            ),
        ]

        register_models(models[0], Capability.TEXT_GENERATION)
        register_models(models[1], Capability.IMAGE_GENERATION)
        all_models = list_models()

        with_params = next((m for m in all_models if m.id == "with-params"), None)
        without_params = next((m for m in all_models if m.id == "without-params"), None)

        assert with_params is not None
        assert len(with_params.supported_parameters) == 2
        assert "feature_a" in with_params.supported_parameters

        assert without_params is not None
        assert len(without_params.supported_parameters) == 0


class TestClear:
    """Test registry clearing functionality."""

    @patch("celeste.registry._load_from_entry_points")
    def test_clear_removes_all_models(self, mock_load: Mock) -> None:
        """clear removes all registered models."""
        # Prevent entry point loading from interfering with test isolation
        mock_load.return_value = None
        register_models(SAMPLE_MODELS[0], Capability.TEXT_GENERATION)
        register_models(SAMPLE_MODELS[1], Capability.IMAGE_GENERATION)
        register_models(SAMPLE_MODELS[2], Capability.TEXT_GENERATION)
        assert len(list_models()) == 3

        clear()
        assert len(list_models()) == 0
        assert get_model("gpt-4", Provider.OPENAI) is None


class TestModel:
    """Test Model class behavior."""

    def test_supported_parameters_computed_from_constraints(self) -> None:
        """supported_parameters property computes from parameter_constraints keys."""
        model = Model(
            id="test-model",
            provider=Provider.OPENAI,
            display_name="Test Model",
            parameter_constraints={"param_a": Str(), "param_b": Str()},
        )

        register_models(model, Capability.TEXT_GENERATION)
        retrieved = get_model("test-model", Provider.OPENAI)

        assert retrieved is not None
        assert len(retrieved.supported_parameters) == 2
        assert "param_a" in retrieved.supported_parameters
        assert "param_b" in retrieved.supported_parameters
        assert "param_c" not in retrieved.supported_parameters

    def test_supported_parameters_empty_by_default(self) -> None:
        """supported_parameters defaults to empty set when parameter_constraints is empty."""
        model = Model(
            id="basic-model",
            provider=Provider.OPENAI,
            display_name="Basic Model",
        )

        register_models(model, Capability.TEXT_GENERATION)
        retrieved = get_model("basic-model", Provider.OPENAI)

        assert retrieved is not None
        assert retrieved.supported_parameters == set()
