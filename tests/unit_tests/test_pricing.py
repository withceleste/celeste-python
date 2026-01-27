"""Tests for the pricing module."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from celeste.core import Provider
from celeste.pricing import (
    Cost,
    calculate_cost,
    clear_pricing,
    get_model_info,
    initialize_pricing,
    is_initialized,
    register_model_pricing,
)
from celeste.pricing.calculator import (
    _calculate_audio_cost,
    _calculate_embedding_cost,
    _calculate_image_cost,
    _calculate_provider_cost,
    _calculate_token_cost,
    _get_tiered_input_cost,
)


class TestCost:
    """Tests for the Cost dataclass."""

    def test_cost_default_values(self) -> None:
        """Test that Cost has correct default values."""
        cost = Cost()
        assert cost.input_cost is None
        assert cost.output_cost is None
        assert cost.cache_creation_cost is None
        assert cost.cache_read_cost is None
        assert cost.reasoning_cost is None
        assert cost.image_cost is None
        assert cost.audio_cost is None
        assert cost.video_cost is None
        assert cost.currency == "USD"

    def test_cost_with_values(self) -> None:
        """Test Cost with provided values."""
        cost = Cost(
            input_cost=0.001,
            output_cost=0.002,
            cache_read_cost=0.0005,
        )
        assert cost.input_cost == 0.001
        assert cost.output_cost == 0.002
        assert cost.cache_read_cost == 0.0005

    def test_total_cost_computes_sum(self) -> None:
        """Test that total_cost computes the sum of all components."""
        cost = Cost(
            input_cost=0.001,
            output_cost=0.002,
            cache_read_cost=0.0005,
        )
        assert cost.total_cost == pytest.approx(0.0035)

    def test_total_cost_with_explicit_total(self) -> None:
        """Test that explicit total takes precedence."""
        cost = Cost(
            input_cost=0.001,
            output_cost=0.002,
            explicit_total=0.01,  # Explicit total
        )
        assert cost.total_cost == 0.01

    def test_total_cost_with_none_values(self) -> None:
        """Test total_cost when some values are None."""
        cost = Cost(
            input_cost=0.001,
            output_cost=None,
            image_cost=0.002,
        )
        assert cost.total_cost == pytest.approx(0.003)

    def test_total_cost_all_none(self) -> None:
        """Test total_cost when all values are None."""
        cost = Cost()
        assert cost.total_cost == 0.0


class TestPricingRegistry:
    """Tests for the pricing registry."""

    def setup_method(self) -> None:
        """Clear pricing state before each test."""
        clear_pricing()

    def test_not_initialized_by_default(self) -> None:
        """Test that pricing is not initialized by default."""
        assert not is_initialized()

    def test_get_model_info_returns_none_when_not_initialized(self) -> None:
        """Test that get_model_info returns None when not initialized."""
        result = get_model_info("gpt-4o", Provider.OPENAI)
        assert result is None

    def test_register_model_pricing(self) -> None:
        """Test that manual pricing registration works."""
        register_model_pricing("test-model", {"input_cost_per_token": 0.001})
        assert is_initialized()

    def test_register_model_pricing_with_lookup(self) -> None:
        """Test that registered pricing can be looked up."""
        register_model_pricing("openai/test-model", {"input_cost_per_token": 0.001})
        result = get_model_info("test-model", Provider.OPENAI)
        assert result is not None
        assert result["input_cost_per_token"] == 0.001

    def test_clear_pricing(self) -> None:
        """Test that clear_pricing resets state."""
        register_model_pricing("test-model", {"input_cost_per_token": 0.001})
        assert is_initialized()
        clear_pricing()
        assert not is_initialized()

    @patch("celeste.pricing.registry.httpx.get")
    def test_initialize_pricing_from_network(self, mock_get: MagicMock) -> None:
        """Test initializing pricing from network."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"gpt-4o": {"input_cost_per_token": 2.5e-6}}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        with (
            tempfile.TemporaryDirectory() as tmpdir,
            patch("celeste.pricing.registry.CACHE_DIR", Path(tmpdir)),
            patch(
                "celeste.pricing.registry.CACHE_FILE",
                Path(tmpdir) / "model_prices.json",
            ),
        ):
            initialize_pricing(force_refresh=True)

        assert is_initialized()
        mock_get.assert_called_once()

    @patch("celeste.pricing.registry.httpx.get")
    def test_initialize_pricing_uses_cache(self, mock_get: MagicMock) -> None:
        """Test that initialize_pricing uses cache when available."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = Path(tmpdir) / "model_prices.json"
            cache_file.write_text(
                json.dumps({"gpt-4o": {"input_cost_per_token": 1e-6}})
            )

            with (
                patch("celeste.pricing.registry.CACHE_DIR", Path(tmpdir)),
                patch("celeste.pricing.registry.CACHE_FILE", cache_file),
            ):
                clear_pricing()
                initialize_pricing()

        assert is_initialized()
        mock_get.assert_not_called()


class TestCostCalculator:
    """Tests for the cost calculator."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        clear_pricing()
        # Register test model pricing
        register_model_pricing(
            "openai/gpt-4o",
            {
                "input_cost_per_token": 2.5e-6,
                "output_cost_per_token": 1.0e-5,
                "cache_read_input_token_cost": 1.25e-6,
                "output_cost_per_reasoning_token": 1.5e-5,
                "mode": "chat",
            },
        )

    def test_calculate_cost_returns_none_when_not_initialized(self) -> None:
        """Test that calculate_cost returns None when pricing not initialized."""
        clear_pricing()
        usage = {"input_tokens": 100, "output_tokens": 50}
        result = calculate_cost(usage, "gpt-4o", Provider.OPENAI)
        assert result is None

    def test_calculate_token_cost_basic(self) -> None:
        """Test basic token cost calculation."""
        usage = {"input_tokens": 1000, "output_tokens": 500}
        model_info = {
            "input_cost_per_token": 2.5e-6,
            "output_cost_per_token": 1.0e-5,
        }
        cost = _calculate_token_cost(usage, model_info)

        assert cost.input_cost == pytest.approx(0.0025)  # 1000 * 2.5e-6
        assert cost.output_cost == pytest.approx(0.005)  # 500 * 1.0e-5

    def test_calculate_token_cost_with_caching(self) -> None:
        """Test token cost calculation with caching."""
        usage = {
            "input_tokens": 1000,
            "output_tokens": 500,
            "cached_tokens": 200,
        }
        model_info = {
            "input_cost_per_token": 2.5e-6,
            "output_cost_per_token": 1.0e-5,
            "cache_read_input_token_cost": 1.25e-6,
        }
        cost = _calculate_token_cost(usage, model_info)

        # 800 regular tokens + 200 cached
        assert cost.input_cost == pytest.approx(0.002)  # 800 * 2.5e-6
        assert cost.cache_read_cost == pytest.approx(0.00025)  # 200 * 1.25e-6

    def test_calculate_token_cost_with_reasoning(self) -> None:
        """Test token cost calculation with reasoning tokens."""
        usage = {
            "input_tokens": 100,
            "output_tokens": 200,
            "reasoning_tokens": 150,
        }
        model_info = {
            "input_cost_per_token": 2.5e-6,
            "output_cost_per_token": 1.0e-5,
            "output_cost_per_reasoning_token": 1.5e-5,
        }
        cost = _calculate_token_cost(usage, model_info)

        assert cost.reasoning_cost == pytest.approx(0.00225)  # 150 * 1.5e-5

    def test_tiered_input_cost_normal(self) -> None:
        """Test normal input cost (under 128k)."""
        model_info = {
            "input_cost_per_token": 2.5e-6,
            "input_cost_per_token_above_128k": 5.0e-6,
        }
        cost = _get_tiered_input_cost(100_000, model_info)
        assert cost == 2.5e-6

    def test_tiered_input_cost_above_128k(self) -> None:
        """Test tiered input cost above 128k."""
        model_info = {
            "input_cost_per_token": 2.5e-6,
            "input_cost_per_token_above_128k": 5.0e-6,
        }
        cost = _get_tiered_input_cost(150_000, model_info)
        assert cost == 5.0e-6

    def test_tiered_input_cost_above_200k(self) -> None:
        """Test tiered input cost above 200k."""
        model_info = {
            "input_cost_per_token": 2.5e-6,
            "input_cost_per_token_above_128k": 5.0e-6,
            "input_cost_per_token_above_200k": 7.5e-6,
        }
        cost = _get_tiered_input_cost(250_000, model_info)
        assert cost == 7.5e-6

    def test_calculate_embedding_cost(self) -> None:
        """Test embedding cost calculation."""
        usage = {"input_tokens": 1000}
        model_info = {"input_cost_per_token": 1e-7}
        cost = _calculate_embedding_cost(usage, model_info)

        assert cost.input_cost == pytest.approx(0.0001)  # 1000 * 1e-7

    def test_calculate_image_cost_per_image(self) -> None:
        """Test image cost calculation per image."""
        usage = {"num_images": 2}
        model_info = {"input_cost_per_image": 0.04}
        cost = _calculate_image_cost(usage, model_info)

        assert cost.image_cost == pytest.approx(0.08)  # 2 * 0.04

    def test_calculate_image_cost_per_pixel(self) -> None:
        """Test image cost calculation per pixel."""
        usage = {"num_images": 1, "width": 1024, "height": 1024}
        model_info = {"input_cost_per_pixel": 1e-8}
        cost = _calculate_image_cost(usage, model_info)

        expected = 1024 * 1024 * 1e-8  # ~0.01
        assert cost.image_cost == pytest.approx(expected)

    def test_calculate_audio_cost_per_character(self) -> None:
        """Test audio cost calculation per character."""
        usage = {"characters": 1000}
        model_info = {"input_cost_per_character": 1.5e-5}
        cost = _calculate_audio_cost(usage, model_info)

        assert cost.audio_cost == pytest.approx(0.015)  # 1000 * 1.5e-5

    def test_calculate_audio_cost_per_second(self) -> None:
        """Test audio cost calculation per second."""
        usage = {"duration_seconds": 60}
        model_info = {"input_cost_per_second": 0.006}
        cost = _calculate_audio_cost(usage, model_info)

        assert cost.audio_cost == pytest.approx(0.36)  # 60 * 0.006

    def test_calculate_provider_cost(self) -> None:
        """Test provider-supplied cost extraction."""
        usage = {"total_cost": 0.05}
        cost = _calculate_provider_cost(usage)

        assert cost.total_cost == 0.05

    def test_calculate_provider_cost_billed_units(self) -> None:
        """Test provider-supplied cost from billed_units."""
        usage = {"billed_units": 0.03}
        cost = _calculate_provider_cost(usage)

        assert cost.total_cost == 0.03

    def test_calculate_cost_full_flow(self) -> None:
        """Test full cost calculation flow."""
        usage = {"input_tokens": 1000, "output_tokens": 500}
        cost = calculate_cost(usage, "gpt-4o", Provider.OPENAI)

        assert cost is not None
        assert cost.input_cost == pytest.approx(0.0025)
        assert cost.output_cost == pytest.approx(0.005)

    def test_calculate_cost_unknown_model(self) -> None:
        """Test cost calculation for unknown model returns None."""
        usage = {"input_tokens": 100}
        cost = calculate_cost(usage, "unknown-model", Provider.OPENAI)
        assert cost is None

    def test_calculate_cost_with_zero_tokens(self) -> None:
        """Test cost calculation with zero tokens."""
        usage = {"input_tokens": 0, "output_tokens": 0}
        cost = calculate_cost(usage, "gpt-4o", Provider.OPENAI)

        assert cost is not None
        # Zero cost values are returned as None
        assert cost.input_cost is None or cost.input_cost == 0
        assert cost.output_cost is None or cost.output_cost == 0


class TestProviderMapping:
    """Tests for provider mapping in registry."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        clear_pricing()

    def test_openai_provider_mapping(self) -> None:
        """Test OpenAI provider maps correctly."""
        register_model_pricing("openai/gpt-4o", {"input_cost_per_token": 1e-6})
        result = get_model_info("gpt-4o", Provider.OPENAI)
        assert result is not None

    def test_anthropic_provider_mapping(self) -> None:
        """Test Anthropic provider maps correctly."""
        register_model_pricing(
            "anthropic/claude-3-opus", {"input_cost_per_token": 1e-6}
        )
        result = get_model_info("claude-3-opus", Provider.ANTHROPIC)
        assert result is not None

    def test_google_provider_mapping(self) -> None:
        """Test Google provider maps to vertex_ai."""
        register_model_pricing("vertex_ai/gemini-pro", {"input_cost_per_token": 1e-6})
        result = get_model_info("gemini-pro", Provider.GOOGLE)
        assert result is not None

    def test_model_without_provider_prefix(self) -> None:
        """Test model lookup without provider prefix."""
        register_model_pricing("gpt-4o", {"input_cost_per_token": 1e-6})
        result = get_model_info("gpt-4o", Provider.OPENAI)
        assert result is not None
