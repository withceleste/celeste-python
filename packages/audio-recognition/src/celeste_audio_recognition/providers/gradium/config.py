"""Gradium provider configuration for audio recognition (STT)."""

# WebSocket URLs (STT/ASR)
EU_STT_WS_URL = "wss://eu.api.gradium.ai/api/speech/asr"
US_STT_WS_URL = "wss://us.api.gradium.ai/api/speech/asr"

# Authentication
AUTH_HEADER_NAME = "x-api-key"

# Audio Input Formats
AUDIO_FORMATS = [
    "pcm",
    "wav",
    "opus",
]
DEFAULT_FORMAT = "pcm"

# Models
DEFAULT_MODEL = "default"

# PCM Audio Specifications (24kHz input for STT)
PCM_SAMPLE_RATE = 24000  # Hz
PCM_BIT_DEPTH = 16  # bits
PCM_CHANNELS = 1  # mono
PCM_CHUNK_SIZE = 1920  # samples (80ms at 24kHz)

# WebSocket message types
WS_MSG_SETUP = "setup"
WS_MSG_READY = "ready"
WS_MSG_AUDIO = "audio"
WS_MSG_TEXT = "text"
WS_MSG_STEP = "step"  # VAD message
WS_MSG_END_TEXT = "end_text"
WS_MSG_END_OF_STREAM = "end_of_stream"
WS_MSG_ERROR = "error"

# WebSocket error codes
WS_ERROR_POLICY_VIOLATION = 1008
WS_ERROR_INTERNAL_SERVER = 1011

# Regions
REGION_EU = "eu"
REGION_US = "us"
DEFAULT_REGION = REGION_EU

__all__ = [
    "AUDIO_FORMATS",
    "AUTH_HEADER_NAME",
    "DEFAULT_FORMAT",
    "DEFAULT_MODEL",
    "DEFAULT_REGION",
    "EU_STT_WS_URL",
    "PCM_BIT_DEPTH",
    "PCM_CHANNELS",
    "PCM_CHUNK_SIZE",
    "PCM_SAMPLE_RATE",
    "REGION_EU",
    "REGION_US",
    "US_STT_WS_URL",
    "WS_ERROR_INTERNAL_SERVER",
    "WS_ERROR_POLICY_VIOLATION",
    "WS_MSG_AUDIO",
    "WS_MSG_END_OF_STREAM",
    "WS_MSG_END_TEXT",
    "WS_MSG_ERROR",
    "WS_MSG_READY",
    "WS_MSG_SETUP",
    "WS_MSG_STEP",
    "WS_MSG_TEXT",
]
