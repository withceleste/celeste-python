"""Google provider configuration for speech generation."""

# HTTP Configuration
BASE_URL = "https://generativelanguage.googleapis.com"
ENDPOINT = "/v1beta/models/{model_id}:generateContent"

# Authentication
AUTH_HEADER_NAME = "x-goog-api-key"
AUTH_HEADER_PREFIX = ""  # Empty string for plain key

# PCM Audio Format Specifications
# Source: Google Gemini TTS docs (ffmpeg -f s16le -ar 24000 -ac 1)
PCM_SAMPLE_RATE = 24000  # Hz
PCM_CHANNELS = 1  # Mono
PCM_SAMPLE_WIDTH = 2  # Bytes (16-bit)
