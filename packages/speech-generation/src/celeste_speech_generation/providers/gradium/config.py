"""Gradium provider configuration for speech generation."""

# Base URLs (REST API)
EU_BASE_URL = "https://eu.api.gradium.ai/api"
US_BASE_URL = "https://us.api.gradium.ai/api"

# WebSocket URLs (TTS)
EU_TTS_WS_URL = "wss://eu.api.gradium.ai/api/speech/tts"
US_TTS_WS_URL = "wss://us.api.gradium.ai/api/speech/tts"

# REST Endpoints
VOICES_ENDPOINT = "/voices/"
VOICE_DETAIL_ENDPOINT = "/voices/{voice_uid}"
CREDITS_ENDPOINT = "/usages/credits"

# Authentication
AUTH_HEADER_NAME = "x-api-key"

# Audio Formats
AUDIO_FORMATS = [
    "wav",
    "pcm",
    "opus",
    "ulaw_8000",
    "alaw_8000",
    "pcm_16000",
    "pcm_24000",
]
DEFAULT_FORMAT = "wav"

# Models
DEFAULT_MODEL = "default"

# Speed control (padding_bonus)
MIN_SPEED = -4.0
MAX_SPEED = 4.0
DEFAULT_SPEED = 0.0

# Break time range (for <break time="X"/> tags)
MIN_BREAK_TIME = 0.1
MAX_BREAK_TIME = 2.0

# PCM Audio Specifications (48kHz output)
PCM_SAMPLE_RATE = 48000  # Hz
PCM_BIT_DEPTH = 16  # bits
PCM_CHANNELS = 1  # mono
PCM_CHUNK_SIZE = 3840  # samples (80ms at 48kHz)

# WebSocket message types
WS_MSG_SETUP = "setup"
WS_MSG_READY = "ready"
WS_MSG_TEXT = "text"
WS_MSG_AUDIO = "audio"
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
    "CREDITS_ENDPOINT",
    "DEFAULT_FORMAT",
    "DEFAULT_MODEL",
    "DEFAULT_REGION",
    "DEFAULT_SPEED",
    "EU_BASE_URL",
    "EU_TTS_WS_URL",
    "MAX_BREAK_TIME",
    "MAX_SPEED",
    "MIN_BREAK_TIME",
    "MIN_SPEED",
    "PCM_BIT_DEPTH",
    "PCM_CHANNELS",
    "PCM_CHUNK_SIZE",
    "PCM_SAMPLE_RATE",
    "REGION_EU",
    "REGION_US",
    "US_BASE_URL",
    "US_TTS_WS_URL",
    "VOICES_ENDPOINT",
    "VOICE_DETAIL_ENDPOINT",
    "WS_ERROR_INTERNAL_SERVER",
    "WS_ERROR_POLICY_VIOLATION",
    "WS_MSG_AUDIO",
    "WS_MSG_END_OF_STREAM",
    "WS_MSG_ERROR",
    "WS_MSG_READY",
    "WS_MSG_SETUP",
    "WS_MSG_TEXT",
]
