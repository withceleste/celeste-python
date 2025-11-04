"""High-value tests for core enums - focusing on critical framework behavior."""

import json
from enum import Enum

import pytest

from celeste.core import Capability, Provider


class TestProvider:
    """Test Provider enum critical behaviors."""

    @pytest.mark.smoke
    def test_provider_is_string_enum(self) -> None:
        """Provider must be a string enum for API compatibility."""
        # Arrange & Act & Assert
        assert issubclass(Provider, str)
        assert issubclass(Provider, Enum)
        # Critical: string comparison must work for API responses
        assert Provider.OPENAI == "openai"  # type: ignore[comparison-overlap]

    def test_provider_json_serialization(self) -> None:
        """Provider must serialize to JSON without custom encoder."""
        # Arrange
        providers = {
            "primary": Provider.ANTHROPIC,
            "fallback": Provider.OPENAI,
        }

        # Act
        json_str = json.dumps(providers)
        loaded = json.loads(json_str)

        # Assert
        assert loaded["primary"] == "anthropic"
        assert loaded["fallback"] == "openai"

    @pytest.mark.parametrize(
        "provider_str,expected",
        [
            ("openai", Provider.OPENAI),
            ("google", Provider.GOOGLE),
            ("anthropic", Provider.ANTHROPIC),
        ],
    )
    def test_provider_from_string(self, provider_str: str, expected: Provider) -> None:
        """Provider can be constructed from string (common API pattern)."""
        # Act
        provider = Provider(provider_str)

        # Assert
        assert provider == expected
        assert provider.value == provider_str

    def test_invalid_provider_raises(self) -> None:
        """Invalid provider string raises ValueError with helpful message."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            Provider("invalid_provider")

        # Verify error message mentions valid options (helps debugging)
        assert "'invalid_provider' is not a valid Provider" in str(exc_info.value)

    def test_provider_case_sensitive(self) -> None:
        """Provider comparison is case-sensitive (API consistency)."""
        # Act & Assert
        assert Provider.OPENAI == "openai"  # type: ignore[comparison-overlap]
        assert Provider.OPENAI != "OpenAI"  # type: ignore[comparison-overlap]
        assert Provider.OPENAI != "OPENAI"


class TestCapability:
    """Test Capability string enum critical behaviors."""

    @pytest.mark.smoke
    def test_capability_is_str_enum(self) -> None:
        """Capability must be a str Enum for string-based capabilities."""
        # Arrange & Act & Assert
        assert issubclass(Capability, Enum)
        assert issubclass(Capability, str)
        # Can create capability from string
        cap = Capability("text_generation")
        assert cap == Capability.TEXT_GENERATION

    def test_capability_set_operations(self) -> None:
        """Capabilities work with set operations (multi-modal support)."""
        # Arrange
        text_only = Capability.TEXT_GENERATION
        image_only = Capability.IMAGE_GENERATION
        multi_modal = {text_only, image_only}

        # Act & Assert - critical for capability checking
        assert text_only in multi_modal
        assert image_only in multi_modal
        assert len(multi_modal) == 2

    def test_capability_values_are_unique(self) -> None:
        """Each capability has a unique string value."""
        # Arrange
        text = Capability.TEXT_GENERATION
        image = Capability.IMAGE_GENERATION

        # Act & Assert
        assert text.value != image.value
        assert text.value == "text_generation"
        assert image.value == "image_generation"

    def test_capability_string_conversion(self) -> None:
        """Capability converts from and to strings correctly."""
        # Arrange & Act
        from_string = Capability("text_generation")
        from_enum = Capability.TEXT_GENERATION

        # Assert
        assert from_string == from_enum
        assert from_enum.value == "text_generation"
        assert from_enum == "text_generation"


class TestEnumImmutability:
    """Test that enums cannot be modified at runtime."""

    def test_cannot_modify_provider_value(self) -> None:
        """Provider enum values are immutable (prevents bugs)."""
        # Act & Assert
        with pytest.raises(AttributeError):
            Provider.OPENAI.value = "modified"  # type: ignore[misc]

    def test_cannot_delete_provider(self) -> None:
        """Cannot delete existing providers (prevents accidental removal)."""
        # Act & Assert
        with pytest.raises(AttributeError):
            del Provider.OPENAI

    def test_cannot_modify_capability_value(self) -> None:
        """Capability enum values are immutable."""
        # Act & Assert
        with pytest.raises(AttributeError):
            Capability.TEXT_GENERATION.value = "modified"  # type: ignore[misc]


class TestEnumUsagePatterns:
    """Test common usage patterns in the framework."""

    def test_provider_in_collection(self) -> None:
        """Provider works correctly in sets and dicts (common pattern)."""
        # Arrange & Act
        providers_set = {Provider.OPENAI, Provider.GOOGLE, Provider.OPENAI}
        provider_config = {
            Provider.OPENAI: {"model": "gpt-4"},
            Provider.GOOGLE: {"model": "gemini"},
        }

        # Assert
        assert len(providers_set) == 2  # Deduplication works
        assert provider_config[Provider.OPENAI]["model"] == "gpt-4"

    def test_capability_empty_set(self) -> None:
        """Can create empty capability set (no capabilities)."""
        # Arrange
        no_caps: set[Capability] = set()  # Empty set of capabilities

        # Act & Assert
        assert Capability.TEXT_GENERATION not in no_caps
        assert Capability.IMAGE_GENERATION not in no_caps
        assert not bool(no_caps)  # Empty set is falsy

    @pytest.mark.parametrize("provider", list(Provider))
    def test_all_providers_are_lowercase(self, provider: Provider) -> None:
        """All provider values are lowercase (API convention)."""
        # Assert
        assert provider.value == provider.value.lower()
        assert provider.value.replace("_", "").isalpha()  # Only letters
