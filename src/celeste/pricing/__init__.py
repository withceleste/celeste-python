"""Pricing module for cost tracking and calculation.

This module provides opt-in cost tracking for API calls. Users must explicitly
call initialize_pricing() to enable cost tracking, which fetches pricing data
from litellm's GitHub repository.

Usage:
    >>> from celeste.pricing import initialize_pricing, CostTracker
    >>> # Opt-in to cost tracking
    >>> initialize_pricing()
    >>> # Create a tracker for session-level tracking
    >>> tracker = CostTracker()
    >>> client = celeste.text.create_client(model="gpt-4o", cost_tracker=tracker)
    >>> await client.generate("Hello")
    >>> print(tracker.total)

Without initialization, cost fields will be None on all outputs:
    >>> result = await celeste.text.generate("Hello", model="gpt-4o")
    >>> print(result.cost)  # None - pricing not initialized
"""

from .calculator import calculate_cost, calculate_video_cost
from .cost import Cost
from .registry import (
    clear_pricing,
    get_model_info,
    get_raw_pricing_data,
    initialize_pricing,
    is_initialized,
    register_model_pricing,
)
from .tracker import CostBreakdown, CostTracker

__all__ = [
    # Cost dataclass
    "Cost",
    # Tracker
    "CostBreakdown",
    "CostTracker",
    # Calculator
    "calculate_cost",
    "calculate_video_cost",
    # Registry functions
    "clear_pricing",
    "get_model_info",
    "get_raw_pricing_data",
    "initialize_pricing",
    "is_initialized",
    "register_model_pricing",
]
