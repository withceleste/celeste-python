"""Configuration for Google CloudTTS API."""

from enum import StrEnum


class GoogleCloudTTSEndpoint(StrEnum):
    """Endpoints for Google CloudTTS API."""

    CREATE_SPEECH = "/v1/text:synthesize"
    LIST_VOICES = "/v1/voices"
    CREATE_LONG_AUDIO = "/v1/{parent=projects/*/locations/*}:synthesizeLongAudio"
    GET_OPERATION = "/v1/{name=projects/*/locations/*/operations/*}"
    LIST_OPERATIONS = "/v1/{name=projects/*/locations/*}/operations"


BASE_URL = "https://texttospeech.googleapis.com"
