"""Gradium-specific types for audio recognition (STT)."""

from pydantic import BaseModel


class VADPrediction(BaseModel):
    """Voice Activity Detection prediction for a specific horizon."""

    horizon_s: float
    inactivity_prob: float


class VADStep(BaseModel):
    """VAD step with predictions for multiple horizons."""

    vad: list[VADPrediction]
    step_idx: int
    step_duration_s: float
    total_duration_s: float


class TranscriptionSegment(BaseModel):
    """Transcribed text segment with timestamps."""

    text: str
    start_s: float
    stop_s: float | None = None
    stream_id: int | None = None


class STTResult(BaseModel):
    """Result from STT transcription."""

    transcription: str
    segments: list[TranscriptionSegment] = []
    vad_steps: list[VADStep] = []
    request_id: str | None = None
    sample_rate: int | None = None
    frame_size: int | None = None


__all__ = [
    "STTResult",
    "TranscriptionSegment",
    "VADPrediction",
    "VADStep",
]
