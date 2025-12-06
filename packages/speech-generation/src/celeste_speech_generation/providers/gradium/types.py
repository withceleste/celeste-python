"""Gradium-specific types for speech generation."""

from pydantic import BaseModel


class VoiceInfo(BaseModel):
    """Voice information from Gradium API."""

    uid: str
    name: str
    description: str | None = None
    language: str | None = None
    start_s: float
    stop_s: float | None = None
    filename: str


class VoiceCreateResponse(BaseModel):
    """Response from voice creation."""

    uid: str | None = None
    error: str | None = None
    was_updated: bool = False


class CreditsSummary(BaseModel):
    """Summary of credits for current billing period."""

    remaining_credits: int
    allocated_credits: int
    billing_period: str
    next_rollover_date: str | None = None
    plan_name: str = ""


class TextWithTimestamp(BaseModel):
    """Text with start and stop timestamps."""

    text: str
    start_s: float
    stop_s: float


class TTSResult(BaseModel):
    """Result from TTS generation."""

    raw_data: bytes
    sample_rate: int
    request_id: str | None = None
    text_with_timestamps: list[TextWithTimestamp] = []


__all__ = [
    "CreditsSummary",
    "TTSResult",
    "TextWithTimestamp",
    "VoiceCreateResponse",
    "VoiceInfo",
]
