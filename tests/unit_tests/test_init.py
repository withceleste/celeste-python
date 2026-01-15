"""High-value tests for celeste.__init__ module."""

from unittest.mock import patch

import pytest
from pydantic import SecretStr

import celeste
from celeste import (
    Capability,
    Modality,
    Model,
    Operation,
    Provider,
    _infer_operation,
    _resolve_model,
    create_client,
)
from celeste.exceptions import ClientNotFoundError, ModelNotFoundError


@pytest.fixture
def sample_models() -> list[Model]:
    """Test models for various scenarios."""
    return [
        Model(
            id="gpt-4",
            provider=Provider.OPENAI,
            capabilities={Capability.TEXT_GENERATION},
            display_name="GPT-4",
        ),
        Model(
            id="claude-3",
            provider=Provider.ANTHROPIC,
            capabilities={Capability.TEXT_GENERATION},
            display_name="Claude 3",
        ),
        Model(
            id="dall-e-3",
            provider=Provider.OPENAI,
            capabilities={Capability.IMAGE_GENERATION},
            display_name="DALL-E 3",
        ),
    ]


class TestCreateClient:
    """Test the create_client factory function."""

    def test_create_client_no_models_available_raises_error(self) -> None:
        """Test that create_client raises ModelNotFoundError when no models are available."""
        with patch("celeste.list_models", autospec=True) as mock_list_models:
            # Arrange
            mock_list_models.return_value = []

            # Act & Assert - capability is translated to modality, so error mentions modality
            with pytest.raises(
                ModelNotFoundError,
                match=r"No model found for modality 'text'",
            ):
                create_client(capability=Capability.TEXT_GENERATION)

    def test_create_client_unregistered_model_creates_fallback_with_warning(
        self,
    ) -> None:
        """Test that unregistered model with provider creates fallback with warning."""
        with (
            patch("celeste.get_model", autospec=True) as mock_get_model,
            patch.dict(celeste._CLIENT_MAP, {}, clear=True),
        ):
            # Arrange
            mock_get_model.return_value = None

            # Act & Assert - should warn and create fallback model
            with (
                pytest.warns(UserWarning, match=r"not registered in Celeste"),
                pytest.raises(ClientNotFoundError),  # No client in _CLIENT_MAP
            ):
                create_client(
                    capability=Capability.TEXT_GENERATION,
                    provider=Provider.OPENAI,
                    model="unregistered-model",
                    api_key=SecretStr("dummy"),
                )

    def test_create_client_uses_explicit_model_when_both_provided(
        self, sample_models: list[Model]
    ) -> None:
        """Test that create_client uses get_model for explicit selection."""
        with (
            patch("celeste.get_model", autospec=True) as mock_get_model,
            patch.dict(celeste._CLIENT_MAP, {}, clear=True),
        ):
            # Arrange
            mock_get_model.return_value = sample_models[1]  # claude-3

            # Act & Assert
            with pytest.raises(ClientNotFoundError):  # No client in _CLIENT_MAP
                create_client(
                    capability=Capability.TEXT_GENERATION,
                    provider=Provider.ANTHROPIC,
                    model="claude-3",
                    api_key=SecretStr("dummy"),
                )

            mock_get_model.assert_called_once_with("claude-3", Provider.ANTHROPIC)

    def test_create_client_string_model_not_found_raises_error(self) -> None:
        """Test that unknown model ID raises ModelNotFoundError."""
        # Act & Assert - model lookup searches all providers, raises if not found
        with pytest.raises(ModelNotFoundError, match=r"Model.*not found"):
            create_client(
                capability=Capability.TEXT_GENERATION,
                model="nonexistent-model",
            )

    def test_create_client_filters_by_provider_when_specified(
        self, sample_models: list[Model]
    ) -> None:
        """Test that provider filtering is applied when provider is specified."""
        with (
            patch("celeste.list_models", autospec=True) as mock_list_models,
            patch.dict(celeste._CLIENT_MAP, {}, clear=True),
        ):
            # Arrange
            mock_list_models.return_value = [sample_models[1]]  # claude-3

            # Act - Should fail at _CLIENT_MAP lookup but provider filtering should work
            with pytest.raises(ClientNotFoundError):  # No client in _CLIENT_MAP
                create_client(
                    capability=Capability.TEXT_GENERATION,
                    provider=Provider.ANTHROPIC,
                    api_key=SecretStr("dummy"),
                )

            # Assert - capability is translated to modality/operation before calling list_models
            mock_list_models.assert_called_once_with(
                provider=Provider.ANTHROPIC,
                modality=Modality.TEXT,
                operation=Operation.GENERATE,
            )


class TestCreateClientIntegration:
    """Test create_client integration with model selection."""

    def test_model_selection_precedence(self, sample_models: list[Model]) -> None:
        """Test that explicit model/provider takes precedence over auto-selection."""
        with (
            patch("celeste.list_models", autospec=True) as mock_list_models,
            patch("celeste.get_model", autospec=True) as mock_get_model,
            patch.dict(celeste._CLIENT_MAP, {}, clear=True),
        ):
            # Arrange
            explicit_model = sample_models[1]  # claude-3
            auto_model = sample_models[0]  # gpt-4

            mock_get_model.return_value = explicit_model
            mock_list_models.return_value = [auto_model]

            # Act - Should fail at _CLIENT_MAP lookup but precedence should work
            with pytest.raises(ClientNotFoundError):
                create_client(
                    capability=Capability.TEXT_GENERATION,
                    provider=Provider.ANTHROPIC,
                    model="claude-3",
                    api_key=SecretStr("dummy"),
                )

            # Assert - Should use explicit path, not auto-selection
            mock_get_model.assert_called_once_with("claude-3", Provider.ANTHROPIC)
            mock_list_models.assert_not_called()  # Should not try auto-selection

    def test_error_propagation_from_registry(self) -> None:
        """Test that errors from registry functions propagate correctly."""
        # Test that registry errors bubble up properly
        with patch("celeste.list_models", autospec=True) as mock_list_models:
            mock_list_models.side_effect = ValueError("Registry error")

            with pytest.raises(ValueError, match="Registry error"):
                create_client(capability=Capability.TEXT_GENERATION)


class TestInferOperation:
    """Test _infer_operation helper function."""

    def test_infer_operation_modality_not_supported(self) -> None:
        """Test that _infer_operation raises when modality is not supported."""
        model = Model(
            id="test-model",
            provider=Provider.OPENAI,
            display_name="Test Model",
            operations={Modality.TEXT: {Operation.GENERATE}},
        )

        with pytest.raises(
            ValueError, match="Model 'test-model' does not support modality 'images'"
        ):
            _infer_operation(model, Modality.IMAGES)

    def test_infer_operation_single_operation_auto_infer(self) -> None:
        """Test that _infer_operation returns the operation when only one is available."""
        model = Model(
            id="test-model",
            provider=Provider.OPENAI,
            display_name="Test Model",
            operations={Modality.TEXT: {Operation.GENERATE}},
        )

        result = _infer_operation(model, Modality.TEXT)
        assert result == Operation.GENERATE

    def test_infer_operation_multiple_operations_requires_explicit(self) -> None:
        """Test that _infer_operation raises when multiple operations are available."""
        model = Model(
            id="test-model",
            provider=Provider.OPENAI,
            display_name="Test Model",
            operations={
                Modality.IMAGES: {Operation.GENERATE, Operation.EDIT},
            },
        )

        with pytest.raises(
            ValueError,
            match=r"Model 'test-model' supports multiple operations for images: .*\. Specify 'operation' explicitly\.",
        ):
            _infer_operation(model, Modality.IMAGES)

    def test_infer_operation_no_operations_error(self) -> None:
        """Test that _infer_operation raises when no operations are registered."""
        model = Model(
            id="test-model",
            provider=Provider.OPENAI,
            display_name="Test Model",
            operations={Modality.TEXT: set()},
        )

        with pytest.raises(
            ValueError,
            match="Model 'test-model' has no registered operations for modality 'text'",
        ):
            _infer_operation(model, Modality.TEXT)


class TestCreateClientModality:
    """Test create_client with modality parameter (new v1 API)."""

    def test_create_client_with_modality_basic(self) -> None:
        """Test basic modality client creation."""
        model = Model(
            id="gpt-4o",
            provider=Provider.OPENAI,
            display_name="GPT-4o",
            operations={Modality.TEXT: {Operation.GENERATE}},
        )

        with (
            patch("celeste.list_models", autospec=True) as mock_list_models,
            patch.dict(celeste._CLIENT_MAP, {}, clear=True),
        ):
            mock_list_models.return_value = [model]

            with pytest.raises(ClientNotFoundError):
                create_client(modality=Modality.TEXT)

            mock_list_models.assert_called_once_with(
                provider=None,
                modality=Modality.TEXT,
                operation=None,
            )

    def test_create_client_with_modality_string_conversion(self) -> None:
        """Test that string modality is converted to Modality enum."""
        model = Model(
            id="gpt-4o",
            provider=Provider.OPENAI,
            display_name="GPT-4o",
            operations={Modality.TEXT: {Operation.GENERATE}},
        )

        with (
            patch("celeste.list_models", autospec=True) as mock_list_models,
            patch.dict(celeste._CLIENT_MAP, {}, clear=True),
        ):
            mock_list_models.return_value = [model]

            with pytest.raises(ClientNotFoundError):
                create_client(modality="text")

            mock_list_models.assert_called_once_with(
                provider=None,
                modality=Modality.TEXT,
                operation=None,
            )

    def test_create_client_with_modality_and_operation(self) -> None:
        """Test create_client with both modality and operation specified."""
        model = Model(
            id="gpt-4o",
            provider=Provider.OPENAI,
            display_name="GPT-4o",
            operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        )

        with (
            patch("celeste.list_models", autospec=True) as mock_list_models,
            patch.dict(celeste._CLIENT_MAP, {}, clear=True),
        ):
            mock_list_models.return_value = [model]

            with pytest.raises(ClientNotFoundError):
                create_client(modality=Modality.TEXT, operation=Operation.ANALYZE)

            mock_list_models.assert_called_once_with(
                provider=None,
                modality=Modality.TEXT,
                operation=Operation.ANALYZE,
            )

    def test_create_client_with_modality_model_resolution(self) -> None:
        """Test that model is resolved correctly with modality."""
        model = Model(
            id="gpt-4o",
            provider=Provider.OPENAI,
            display_name="GPT-4o",
            operations={Modality.TEXT: {Operation.GENERATE}},
        )

        with (
            patch("celeste.get_model", autospec=True) as mock_get_model,
            patch.dict(celeste._CLIENT_MAP, {}, clear=True),
        ):
            mock_get_model.return_value = model

            with pytest.raises(ClientNotFoundError):
                create_client(modality=Modality.TEXT, model="gpt-4o")

            mock_get_model.assert_called_once_with("gpt-4o", None)


class TestResolveModel:
    """Test _resolve_model helper function."""

    def test_resolve_model_no_modality_raises(self) -> None:
        """Test that _resolve_model raises when modality not provided."""
        with pytest.raises(
            ValueError,
            match="Either 'modality' or 'model' must be provided",
        ):
            _resolve_model()

    def test_resolve_model_with_modality_no_models_raises(self) -> None:
        """Test that _resolve_model raises ModelNotFoundError when no models found."""
        with patch("celeste.list_models", autospec=True) as mock_list_models:
            mock_list_models.return_value = []
            with pytest.raises(ModelNotFoundError):
                _resolve_model(modality=Modality.TEXT)

    def test_resolve_model_with_modality_returns_first_model(self) -> None:
        """Test that _resolve_model returns first model when multiple available."""
        model1 = Model(
            id="model-1",
            provider=Provider.OPENAI,
            display_name="Model 1",
            operations={Modality.TEXT: {Operation.GENERATE}},
        )
        model2 = Model(
            id="model-2",
            provider=Provider.OPENAI,
            display_name="Model 2",
            operations={Modality.TEXT: {Operation.GENERATE}},
        )
        with patch("celeste.list_models", autospec=True) as mock_list_models:
            mock_list_models.return_value = [model1, model2]
            result = _resolve_model(modality=Modality.TEXT)
            assert result == model1

    def test_resolve_model_string_model_not_found_no_provider_raises(self) -> None:
        """Test that _resolve_model raises ModelNotFoundError for string model without provider."""
        with patch("celeste.get_model", autospec=True) as mock_get_model:
            mock_get_model.return_value = None
            with pytest.raises(ModelNotFoundError):
                _resolve_model(model="nonexistent-model")

    def test_resolve_model_string_model_not_found_with_provider_creates_fallback(
        self,
    ) -> None:
        """Test that _resolve_model creates fallback model when string model not found with provider."""
        with (
            patch("celeste.get_model", autospec=True) as mock_get_model,
            pytest.warns(UserWarning, match=r"not registered in Celeste"),
        ):
            mock_get_model.return_value = None
            result = _resolve_model(
                model="unregistered-model",
                provider=Provider.OPENAI,
                modality=Modality.TEXT,
            )
            assert result.id == "unregistered-model"
            assert result.provider == Provider.OPENAI
            assert Modality.TEXT in result.operations

    def test_resolve_model_string_model_not_found_no_modality_raises(
        self,
    ) -> None:
        """Test that _resolve_model raises ValueError when model not found and no modality."""
        with (
            patch("celeste.get_model", autospec=True) as mock_get_model,
        ):
            mock_get_model.return_value = None
            with pytest.raises(
                ValueError,
                match=r"Model 'nonexistent' not registered. Specify 'modality' explicitly\.",
            ):
                _resolve_model(model="nonexistent", provider=Provider.OPENAI)

    def test_resolve_model_returns_model_object_directly(self) -> None:
        """Test that _resolve_model returns Model object when passed directly."""
        model = Model(
            id="test-model",
            provider=Provider.OPENAI,
            display_name="Test Model",
            operations={Modality.TEXT: {Operation.GENERATE}},
        )
        result = _resolve_model(model=model)
        assert result == model
