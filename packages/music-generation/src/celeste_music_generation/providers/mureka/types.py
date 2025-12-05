"""Mureka-specific types for extended functionality."""

from pydantic import BaseModel


class LyricsOutput(BaseModel):
    """Output for lyrics generation and extension."""

    title: str | None = None
    lyrics: str


class SongDescription(BaseModel):
    """Description of a song's characteristics."""

    instruments: list[str]
    genres: list[str]
    tags: list[str]
    description: str


class StemOutput(BaseModel):
    """Output for song stemming (track separation)."""

    zip_url: str
    expires_at: int  # Unix timestamp in seconds


class BillingInfo(BaseModel):
    """Account billing information."""

    account_id: int
    balance: int  # in cents
    total_recharge: int  # in cents
    total_spending: int  # in cents
    concurrent_request_limit: int


__all__ = [
    "BillingInfo",
    "LyricsOutput",
    "SongDescription",
    "StemOutput",
]
