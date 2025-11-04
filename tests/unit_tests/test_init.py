"""High-value tests for celeste.__init__ module."""

from unittest.mock import patch

import pytest

from celeste import Capability, Model, Provider, create_client


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
        """Test that create_client raises ValueError when no models are available."""
        with patch("celeste.list_models", autospec=True) as mock_list_models:
            # Arrange
            mock_list_models.return_value = []

            # Act & Assert
            with pytest.raises(
                ValueError, match=r"No model found for.*text_generation"
            ):
                create_client(capability=Capability.TEXT_GENERATION)

    def test_create_client_specific_model_not_found_raises_error(self) -> None:
        """Test error when specific model/provider combination doesn't exist."""
        with patch("celeste.get_model", autospec=True) as mock_get_model:
            # Arrange
            mock_get_model.return_value = None

            # Act & Assert
            with pytest.raises(ValueError, match=r"Model.*not found"):
                create_client(
                    capability=Capability.TEXT_GENERATION,
                    provider=Provider.OPENAI,
                    model="nonexistent-model",
                )

    def test_create_client_uses_explicit_model_when_both_provided(
        self, sample_models: list[Model]
    ) -> None:
        """Test that create_client uses get_model for explicit selection."""
        with patch("celeste.get_model", autospec=True) as mock_get_model:
            # Arrange
            mock_get_model.return_value = sample_models[1]  # claude-3

            # Act & Assert
            with pytest.raises(
                NotImplementedError
            ):  # _get_client_class not implemented
                create_client(
                    capability=Capability.TEXT_GENERATION,
                    provider=Provider.ANTHROPIC,
                    model="claude-3",
                )

            mock_get_model.assert_called_once_with("claude-3", Provider.ANTHROPIC)

    def test_create_client_string_model_without_provider_raises_error(self) -> None:
        """Test that string model ID without provider raises ValueError."""
        # Act & Assert
        with pytest.raises(
            ValueError, match="provider required when model is a string ID"
        ):
            create_client(
                capability=Capability.TEXT_GENERATION,
                model="some-model",  # provider=None - should error
            )

    def test_create_client_filters_by_provider_when_specified(
        self, sample_models: list[Model]
    ) -> None:
        """Test that provider filtering is applied when provider is specified."""
        with patch("celeste.list_models", autospec=True) as mock_list_models:
            # Arrange
            mock_list_models.return_value = [sample_models[1]]  # claude-3

            # Act - Should fail at _get_client_class but provider filtering should work
            with pytest.raises(
                NotImplementedError
            ):  # _get_client_class not implemented
                create_client(
                    capability=Capability.TEXT_GENERATION,
                    provider=Provider.ANTHROPIC,
                )

            # Assert - verify provider was passed to list_models
            mock_list_models.assert_called_once_with(
                provider=Provider.ANTHROPIC, capability=Capability.TEXT_GENERATION
            )


class TestCreateClientIntegration:
    """Test create_client integration with model selection."""

    def test_model_selection_precedence(self, sample_models: list[Model]) -> None:
        """Test that explicit model/provider takes precedence over auto-selection."""
        with (
            patch("celeste.list_models", autospec=True) as mock_list_models,
            patch("celeste.get_model", autospec=True) as mock_get_model,
        ):
            # Arrange
            explicit_model = sample_models[1]  # claude-3
            auto_model = sample_models[0]  # gpt-4

            mock_get_model.return_value = explicit_model
            mock_list_models.return_value = [auto_model]

            # Act - Should fail at _get_client_class but precedence should work
            with pytest.raises(NotImplementedError):
                create_client(
                    capability=Capability.TEXT_GENERATION,
                    provider=Provider.ANTHROPIC,
                    model="claude-3",
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
