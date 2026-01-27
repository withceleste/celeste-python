"""Pricing registry for model cost data.

Provides opt-in pricing data loading from litellm's GitHub repository.
Users must explicitly call initialize_pricing() to enable cost tracking.
"""

from __future__ import annotations

import json
import warnings
from datetime import datetime, timedelta
from pathlib import Path

import httpx

from celeste.core import Provider

LITELLM_PRICING_URL = (
    "https://raw.githubusercontent.com/BerriAI/litellm/main/"
    "model_prices_and_context_window.json"
)
CACHE_DIR = Path.home() / ".cache" / "celeste"
CACHE_FILE = CACHE_DIR / "model_prices.json"
CACHE_TTL = timedelta(hours=24)

# Module-level state
_model_prices: dict[str, dict] = {}
_initialized: bool = False


def initialize_pricing(force_refresh: bool = False) -> None:
    """Initialize pricing data. Must be called explicitly by user.

    This is the ONLY function that makes network requests.
    Users must call this to enable cost tracking.

    The function fetches pricing data from litellm's GitHub repository
    and caches it locally for 24 hours.

    Args:
        force_refresh: If True, fetch fresh data even if cache is valid.

    Raises:
        No exceptions are raised - failures result in warnings and
        fallback to stale cache if available.
    """
    global _model_prices, _initialized

    # Check local cache first (no network)
    if not force_refresh and CACHE_FILE.exists():
        cache_age = datetime.now() - datetime.fromtimestamp(CACHE_FILE.stat().st_mtime)
        if cache_age < CACHE_TTL:
            try:
                _model_prices = json.loads(CACHE_FILE.read_text())
                _initialized = True
                return
            except (json.JSONDecodeError, OSError) as e:
                warnings.warn(
                    f"Failed to read pricing cache: {e}",
                    UserWarning,
                    stacklevel=2,
                )

    # Fetch from GitHub (network call)
    try:
        response = httpx.get(LITELLM_PRICING_URL, timeout=10.0)
        response.raise_for_status()
        _model_prices = response.json()

        # Update cache
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(json.dumps(_model_prices))
        _initialized = True
    except Exception as e:
        warnings.warn(
            f"Failed to fetch pricing data: {e}",
            UserWarning,
            stacklevel=2,
        )
        # Try stale cache as fallback
        if CACHE_FILE.exists():
            try:
                _model_prices = json.loads(CACHE_FILE.read_text())
                _initialized = True
                warnings.warn(
                    "Using stale pricing cache as fallback",
                    UserWarning,
                    stacklevel=2,
                )
            except (json.JSONDecodeError, OSError):
                pass


def is_initialized() -> bool:
    """Check if pricing data has been loaded.

    Returns:
        True if pricing data is available (either from fetch or manual registration).
    """
    return _initialized


def get_model_info(model_id: str, provider: Provider) -> dict | None:
    """Get pricing info for a model.

    Args:
        model_id: The model identifier (e.g., "gpt-4o", "claude-3-opus").
        provider: The provider enum.

    Returns:
        Dictionary with pricing info if found, None otherwise.
        Returns None silently if pricing not initialized (user hasn't opted in)
        or if model not found (with warning).
    """
    if not _initialized:
        return None  # Silent return - user hasn't opted in

    # Map Provider enum to litellm provider prefix
    provider_map: dict[Provider, str] = {
        Provider.OPENAI: "openai",
        Provider.ANTHROPIC: "anthropic",
        Provider.GOOGLE: "vertex_ai",  # litellm uses vertex_ai for Google
        Provider.MISTRAL: "mistral",
        Provider.GROQ: "groq",
        Provider.XAI: "xai",
        Provider.BFL: "bfl",  # Black Forest Labs
        Provider.DEEPSEEK: "deepseek",
        Provider.OLLAMA: "ollama",
        Provider.ELEVENLABS: "elevenlabs",
        Provider.LUMA: "luma",
        Provider.COHERE: "cohere",
        Provider.PERPLEXITY: "perplexity",
        Provider.REPLICATE: "replicate",
        Provider.HUGGINGFACE: "huggingface",
        Provider.STABILITYAI: "stability_ai",
    }

    provider_prefix = provider_map.get(provider, provider.value)

    # Try provider/model format first (most specific)
    key = f"{provider_prefix}/{model_id}"
    if key in _model_prices:
        return _model_prices[key]

    # Try model_id alone (some models are provider-independent)
    if model_id in _model_prices:
        return _model_prices[model_id]

    # Try common aliases (e.g., "gpt-4o" might be stored as "gpt-4o-2024-05-13")
    # Also try without version suffixes
    base_model = model_id.rsplit("-", 1)[0] if "-" in model_id else None
    if base_model:
        key = f"{provider_prefix}/{base_model}"
        if key in _model_prices:
            return _model_prices[key]
        if base_model in _model_prices:
            return _model_prices[base_model]

    return None


def register_model_pricing(key: str, pricing: dict) -> None:
    """Register custom pricing at runtime (no network call).

    Use this to add pricing for models not in litellm's database,
    such as local Ollama models or custom deployments.

    Args:
        key: The model key (e.g., "ollama/llama2" or just "llama2").
        pricing: Dictionary with pricing info following litellm's format:
            - input_cost_per_token: Cost per input token
            - output_cost_per_token: Cost per output token
            - cache_read_input_token_cost: Cost for cached input tokens
            - output_cost_per_reasoning_token: Cost for reasoning tokens
            - input_cost_per_image: Cost per image
            - input_cost_per_second: Cost per second (audio/video)

    Example:
        >>> register_model_pricing(
        ...     "ollama/llama2",
        ...     {
        ...         "input_cost_per_token": 0.0,
        ...         "output_cost_per_token": 0.0,
        ...     },
        ... )
    """
    global _initialized
    _model_prices[key] = pricing
    _initialized = True  # Manual registration counts as initialized


def clear_pricing() -> None:
    """Clear all pricing data and reset initialization state.

    Primarily for testing purposes.
    """
    global _model_prices, _initialized
    _model_prices = {}
    _initialized = False


def get_raw_pricing_data() -> dict[str, dict]:
    """Get the raw pricing data dictionary.

    Returns a copy to prevent modification of internal state.

    Returns:
        Copy of the pricing data dictionary.
    """
    return _model_prices.copy()


__all__ = [
    "CACHE_DIR",
    "CACHE_FILE",
    "CACHE_TTL",
    "LITELLM_PRICING_URL",
    "clear_pricing",
    "get_model_info",
    "get_raw_pricing_data",
    "initialize_pricing",
    "is_initialized",
    "register_model_pricing",
]
