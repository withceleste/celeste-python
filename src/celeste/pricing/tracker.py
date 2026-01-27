"""Cost tracking for session-level cost aggregation.

Provides thread-safe tracking of cumulative costs across multiple API calls.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any

from .cost import Cost


@dataclass
class CostBreakdown:
    """Breakdown of costs by category."""

    input: float = 0.0
    output: float = 0.0
    cache_creation: float = 0.0
    cache_read: float = 0.0
    reasoning: float = 0.0
    image: float = 0.0
    audio: float = 0.0
    video: float = 0.0

    @property
    def total(self) -> float:
        """Sum all cost categories."""
        return (
            self.input
            + self.output
            + self.cache_creation
            + self.cache_read
            + self.reasoning
            + self.image
            + self.audio
            + self.video
        )

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary."""
        return {
            "input": self.input,
            "output": self.output,
            "cache_creation": self.cache_creation,
            "cache_read": self.cache_read,
            "reasoning": self.reasoning,
            "image": self.image,
            "audio": self.audio,
            "video": self.video,
            "total": self.total,
        }


@dataclass
class CostTracker:
    """Track cumulative costs across multiple API calls.

    Thread-safe for concurrent usage in async contexts.

    Example:
        >>> from celeste.pricing import CostTracker, initialize_pricing
        >>> initialize_pricing()
        >>> tracker = CostTracker()
        >>> client = celeste.text.create_client(model="gpt-4o", cost_tracker=tracker)
        >>> await client.generate("Hello")
        >>> await client.generate("World")
        >>> print(tracker.total)  # Cumulative cost
        >>> print(tracker.breakdown)  # By category
    """

    _costs: list[Cost] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    currency: str = "USD"

    def add(self, cost: Cost | None) -> None:
        """Add a cost to the tracker.

        Args:
            cost: Cost object to add. None values are ignored.
        """
        if cost is None:
            return

        with self._lock:
            self._costs.append(cost)

    @property
    def total(self) -> float:
        """Get total cumulative cost.

        Returns:
            Sum of all tracked costs in USD.
        """
        with self._lock:
            return sum(c.total_cost for c in self._costs)

    @property
    def breakdown(self) -> CostBreakdown:
        """Get cost breakdown by category.

        Returns:
            CostBreakdown with sums for each cost type.
        """
        with self._lock:
            breakdown = CostBreakdown()
            for cost in self._costs:
                if cost.input_cost is not None:
                    breakdown.input += cost.input_cost
                if cost.output_cost is not None:
                    breakdown.output += cost.output_cost
                if cost.cache_creation_cost is not None:
                    breakdown.cache_creation += cost.cache_creation_cost
                if cost.cache_read_cost is not None:
                    breakdown.cache_read += cost.cache_read_cost
                if cost.reasoning_cost is not None:
                    breakdown.reasoning += cost.reasoning_cost
                if cost.image_cost is not None:
                    breakdown.image += cost.image_cost
                if cost.audio_cost is not None:
                    breakdown.audio += cost.audio_cost
                if cost.video_cost is not None:
                    breakdown.video += cost.video_cost
            return breakdown

    @property
    def count(self) -> int:
        """Get number of tracked costs.

        Returns:
            Number of Cost objects added to the tracker.
        """
        with self._lock:
            return len(self._costs)

    def reset(self) -> None:
        """Clear all tracked costs."""
        with self._lock:
            self._costs.clear()

    def get_costs(self) -> list[Cost]:
        """Get a copy of all tracked costs.

        Returns:
            List of all Cost objects added to the tracker.
        """
        with self._lock:
            return self._costs.copy()

    def to_dict(self) -> dict[str, Any]:
        """Convert tracker state to dictionary.

        Returns:
            Dictionary with total, breakdown, count, and currency.
        """
        return {
            "total": self.total,
            "breakdown": self.breakdown.to_dict(),
            "count": self.count,
            "currency": self.currency,
        }


__all__ = [
    "CostBreakdown",
    "CostTracker",
]
