"""Cost calculation logic for API calls.

Supports various pricing models:
- Token-based pricing (input/output tokens)
- Tiered pricing (above 128k, 200k tokens)
- Prompt caching discounts
- Reasoning tokens (o1, etc.)
- Per-image pricing
- Per-pixel pricing
- Per-second pricing (audio/video)
- Per-character pricing (Vertex AI)
- Provider-supplied cost (BFL)
"""

from __future__ import annotations

from typing import Any

from celeste.core import Provider

from .cost import Cost
from .registry import get_model_info


def calculate_cost(
    usage: dict[str, Any],
    model_id: str,
    provider: Provider,
    model_info: dict[str, Any] | None = None,
) -> Cost | None:
    """Calculate cost from usage data and pricing information.

    Args:
        usage: Dictionary with usage metrics (input_tokens, output_tokens, etc.).
        model_id: The model identifier.
        provider: The provider enum.
        model_info: Optional pre-fetched pricing info. If None, will be looked up.

    Returns:
        Cost object with breakdown, or None if pricing not available.
    """
    if model_info is None:
        model_info = get_model_info(model_id, provider)

    if model_info is None:
        return None

    # Check for provider-supplied cost (e.g., BFL)
    if model_info.get("uses_provider_cost"):
        return _calculate_provider_cost(usage)

    # Determine pricing mode
    mode = model_info.get("mode", "chat")

    if mode == "embedding":
        return _calculate_embedding_cost(usage, model_info)
    elif mode == "image_generation":
        return _calculate_image_cost(usage, model_info)
    elif mode == "audio_speech":
        return _calculate_audio_cost(usage, model_info)
    else:
        # Default to token-based (chat, completion, etc.)
        return _calculate_token_cost(usage, model_info)


def _calculate_token_cost(usage: dict[str, Any], model_info: dict) -> Cost:
    """Calculate cost for token-based models (chat, completion).

    Handles:
    - Standard input/output token pricing
    - Tiered pricing for large contexts (128k+, 200k+ tokens)
    - Prompt caching (creation and read costs)
    - Reasoning tokens (o1, etc.)
    """
    input_tokens = usage.get("input_tokens", 0) or 0
    output_tokens = usage.get("output_tokens", 0) or 0
    cached_tokens = (
        usage.get("cached_tokens", 0) or usage.get("cache_read_input_tokens", 0) or 0
    )
    cache_creation_tokens = usage.get("cache_creation_input_tokens", 0) or 0
    reasoning_tokens = usage.get("reasoning_tokens", 0) or 0

    # Determine input cost per token (with tiered pricing support)
    input_cost_per_token = _get_tiered_input_cost(input_tokens, model_info)

    # Calculate input cost (subtract cached tokens as they have different rate)
    billable_input_tokens = max(0, input_tokens - cached_tokens - cache_creation_tokens)
    input_cost = billable_input_tokens * input_cost_per_token

    # Calculate cache costs
    cache_read_cost = None
    if cached_tokens > 0:
        cache_read_rate = model_info.get("cache_read_input_token_cost", 0)
        cache_read_cost = cached_tokens * cache_read_rate

    cache_creation_cost = None
    if cache_creation_tokens > 0:
        cache_creation_rate = model_info.get(
            "cache_creation_input_token_cost", input_cost_per_token
        )
        cache_creation_cost = cache_creation_tokens * cache_creation_rate

    # Calculate output cost
    output_cost_per_token = model_info.get("output_cost_per_token", 0)
    output_cost = output_tokens * output_cost_per_token

    # Calculate reasoning cost (separate from regular output for o1 models)
    reasoning_cost = None
    if reasoning_tokens > 0:
        reasoning_cost_per_token = model_info.get(
            "output_cost_per_reasoning_token", output_cost_per_token
        )
        reasoning_cost = reasoning_tokens * reasoning_cost_per_token

    return Cost(
        input_cost=input_cost if input_cost > 0 else None,
        output_cost=output_cost if output_cost > 0 else None,
        cache_creation_cost=cache_creation_cost,
        cache_read_cost=cache_read_cost,
        reasoning_cost=reasoning_cost,
    )


def _get_tiered_input_cost(input_tokens: int, model_info: dict) -> float:
    """Get input cost per token, considering tiered pricing.

    litellm supports tiered pricing for large contexts:
    - input_cost_per_token: Default rate
    - input_cost_per_token_above_128k: Rate for tokens above 128k
    - input_cost_per_token_above_200k: Rate for tokens above 200k (Gemini)
    """
    # Check for tiered pricing (highest tier first)
    if input_tokens > 200_000 and "input_cost_per_token_above_200k" in model_info:
        return float(model_info["input_cost_per_token_above_200k"])
    if input_tokens > 128_000 and "input_cost_per_token_above_128k" in model_info:
        return float(model_info["input_cost_per_token_above_128k"])

    return float(model_info.get("input_cost_per_token", 0))


def _calculate_embedding_cost(usage: dict[str, Any], model_info: dict) -> Cost:
    """Calculate cost for embedding models.

    Embeddings typically only have input tokens.
    """
    input_tokens = usage.get("input_tokens", 0) or usage.get("total_tokens", 0) or 0
    input_cost_per_token = model_info.get("input_cost_per_token", 0)
    input_cost = input_tokens * input_cost_per_token

    return Cost(
        input_cost=input_cost if input_cost > 0 else None,
    )


def _calculate_image_cost(usage: dict[str, Any], model_info: dict) -> Cost:
    """Calculate cost for image generation models.

    Supports multiple pricing models:
    - Per-image: input_cost_per_image
    - Per-pixel: input_cost_per_pixel (width * height)
    - Per-megapixel: Based on image dimensions
    - Token-based: Some models (like GPT-4 vision) use tokens
    """
    image_cost = None

    # Per-image pricing (most common for generation)
    num_images = usage.get("num_images", 1) or 1
    if "input_cost_per_image" in model_info:
        cost_per_image = model_info["input_cost_per_image"]
        image_cost = num_images * cost_per_image

    # Per-pixel pricing
    elif "input_cost_per_pixel" in model_info:
        width = usage.get("width", 0) or 0
        height = usage.get("height", 0) or 0
        if width > 0 and height > 0:
            pixels = width * height * num_images
            image_cost = pixels * model_info["input_cost_per_pixel"]

    # Per-megapixel pricing (for outputs)
    elif "output_mp" in usage:
        output_mp = usage.get("output_mp", 0) or 0
        # Some providers charge per megapixel
        if "output_cost_per_megapixel" in model_info:
            image_cost = output_mp * model_info["output_cost_per_megapixel"]

    # Billed units (provider-specific like BFL)
    elif "billed_units" in usage:
        billed_units = usage.get("billed_units", 0) or 0
        if "cost_per_billed_unit" in model_info:
            image_cost = billed_units * model_info["cost_per_billed_unit"]
        else:
            # Assume billed_units is already the cost in some currency unit
            image_cost = billed_units

    # Token-based image models (GPT-4 vision input)
    if "input_tokens" in usage and "input_cost_per_token" in model_info:
        input_tokens = usage.get("input_tokens", 0) or 0
        input_cost = input_tokens * model_info["input_cost_per_token"]
        return Cost(
            input_cost=input_cost if input_cost > 0 else None,
            image_cost=image_cost,
        )

    return Cost(
        image_cost=image_cost,
    )


def _calculate_audio_cost(usage: dict[str, Any], model_info: dict) -> Cost:
    """Calculate cost for audio models (TTS, STT).

    Supports:
    - Per-character pricing (common for TTS)
    - Per-second pricing (for audio duration)
    - Token-based pricing
    """
    audio_cost = None

    # Per-character pricing (TTS)
    if "characters" in usage and "input_cost_per_character" in model_info:
        characters = usage.get("characters", 0) or 0
        audio_cost = characters * model_info["input_cost_per_character"]

    # Per-second pricing (audio duration)
    elif "duration_seconds" in usage and "input_cost_per_second" in model_info:
        duration = usage.get("duration_seconds", 0) or 0
        audio_cost = duration * model_info["input_cost_per_second"]

    # Token-based audio models (Whisper)
    if "input_tokens" in usage and "input_cost_per_token" in model_info:
        input_tokens = usage.get("input_tokens", 0) or 0
        input_cost = input_tokens * model_info["input_cost_per_token"]
        return Cost(
            input_cost=input_cost if input_cost > 0 else None,
            audio_cost=audio_cost,
        )

    return Cost(
        audio_cost=audio_cost,
    )


def _calculate_provider_cost(usage: dict[str, Any]) -> Cost:
    """Extract provider-supplied cost from usage.

    Some providers (like BFL) return cost directly in the response.
    """
    # Look for common cost fields in usage
    total_cost = (
        usage.get("total_cost") or usage.get("cost") or usage.get("billed_units")
    )

    if total_cost is not None:
        return Cost(explicit_total=float(total_cost))

    return Cost()


def calculate_video_cost(usage: dict[str, Any], model_info: dict) -> Cost:
    """Calculate cost for video generation models.

    Supports:
    - Per-second pricing
    - Per-frame pricing
    - Resolution-based pricing
    """
    video_cost = None

    # Per-second pricing
    if "duration_seconds" in usage and "input_cost_per_second" in model_info:
        duration = usage.get("duration_seconds", 0) or 0
        video_cost = duration * model_info["input_cost_per_second"]

    # Per-frame pricing
    elif "num_frames" in usage and "input_cost_per_frame" in model_info:
        num_frames = usage.get("num_frames", 0) or 0
        video_cost = num_frames * model_info["input_cost_per_frame"]

    return Cost(
        video_cost=video_cost,
    )


__all__ = [
    "calculate_cost",
    "calculate_video_cost",
]
