"""Cost dataclass for API call cost breakdowns."""

from typing import Any

from pydantic import BaseModel, Field, PrivateAttr, computed_field


class Cost(BaseModel):
    """Cost breakdown for an API call. All values in USD.

    This class captures detailed cost information from API calls, supporting
    various pricing models including token-based, per-image, per-second,
    and provider-specific pricing.

    All fields are optional since not all providers return all cost components.
    """

    # Token-based costs
    input_cost: float | None = Field(default=None, description="Cost for input tokens")
    output_cost: float | None = Field(
        default=None, description="Cost for output tokens"
    )
    cache_creation_cost: float | None = Field(
        default=None, description="Cost to write to cache"
    )
    cache_read_cost: float | None = Field(
        default=None, description="Discounted cost for cache hits"
    )
    reasoning_cost: float | None = Field(
        default=None, description="Cost for reasoning tokens (o1, etc.)"
    )

    # Modality-specific costs
    image_cost: float | None = Field(default=None, description="Cost for images")
    audio_cost: float | None = Field(default=None, description="Cost for audio")
    video_cost: float | None = Field(default=None, description="Cost for video")

    # Currency
    currency: str = "USD"

    # Private attribute for caching explicit total
    _explicit_total: float | None = PrivateAttr(default=None)

    def __init__(self, *, explicit_total: float | None = None, **data: Any) -> None:  # noqa: ANN401
        """Initialize Cost with optional explicit total.

        Args:
            explicit_total: If provided, this value is returned as total_cost
                           instead of computing from components.
            **data: Other field values.
        """
        super().__init__(**data)
        self._explicit_total = explicit_total

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_cost(self) -> float:
        """Sum all non-None cost components.

        Returns the explicit total if set during initialization,
        otherwise computes the sum of all individual cost components.

        Returns:
            Total cost in USD.
        """
        if self._explicit_total is not None:
            return self._explicit_total
        components = [
            self.input_cost,
            self.output_cost,
            self.cache_creation_cost,
            self.cache_read_cost,
            self.reasoning_cost,
            self.image_cost,
            self.audio_cost,
            self.video_cost,
        ]
        return sum(c for c in components if c is not None)


__all__ = ["Cost"]
