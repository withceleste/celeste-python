"""ElevenLabs audio client (dispatches TTS and STT wire backends)."""

from typing import Any, Unpack

from celeste.parameters import ParameterMapper
from celeste.types import AudioContent

from ...client import AudioClient
from ...io import AudioInput
from ...parameters import AudioParameters
from ...streaming import AudioStream
from .models import ELEVENLABS_STT_MODELS, ELEVENLABS_TTS_MODELS
from .parameters import (
    ELEVENLABS_SPEECH_TO_TEXT_PARAMETER_MAPPERS,
    ELEVENLABS_TEXT_TO_SPEECH_PARAMETER_MAPPERS,
)
from .speech_to_text import ElevenLabsSpeechToTextAudioClient
from .text_to_speech import ElevenLabsTextToSpeechAudioClient

_TTS_MODEL_IDS = frozenset(m.id for m in ELEVENLABS_TTS_MODELS)
_STT_MODEL_IDS = frozenset(m.id for m in ELEVENLABS_STT_MODELS)


class ElevenLabsAudioClient(AudioClient):
    """ElevenLabs audio client (selects TTS or STT backend by model id)."""

    _strategy: (
        ElevenLabsTextToSpeechAudioClient | ElevenLabsSpeechToTextAudioClient | None
    ) = None

    def model_post_init(self, __context: object) -> None:
        """Select the backend once by model id."""
        super().model_post_init(__context)

        StrategyClass: type[AudioClient]
        if self.model.id in _TTS_MODEL_IDS:
            StrategyClass = ElevenLabsTextToSpeechAudioClient
        elif self.model.id in _STT_MODEL_IDS:
            StrategyClass = ElevenLabsSpeechToTextAudioClient
        else:
            msg = f"Unknown ElevenLabs audio model: {self.model.id}"
            raise ValueError(msg)

        strategy = StrategyClass(
            modality=self.modality,
            model=self.model,
            provider=self.provider,
            auth=self.auth,
            base_url=self.base_url,
        )
        object.__setattr__(self, "_strategy", strategy)

        if strategy._speak_endpoint is not None:
            object.__setattr__(self, "_speak_endpoint", strategy._speak_endpoint)
        if strategy._transcribe_endpoint is not None:
            object.__setattr__(
                self, "_transcribe_endpoint", strategy._transcribe_endpoint
            )

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[AudioContent]]:
        return [
            *ELEVENLABS_TEXT_TO_SPEECH_PARAMETER_MAPPERS,
            *ELEVENLABS_SPEECH_TO_TEXT_PARAMETER_MAPPERS,
        ]

    def _init_request(self, inputs: AudioInput) -> dict[str, Any]:
        return self._strategy._init_request(inputs)  # type: ignore[union-attr]

    def _build_request(
        self,
        inputs: AudioInput,
        extra_body: dict[str, Any] | None = None,
        streaming: bool = False,
        **parameters: Unpack[AudioParameters],
    ) -> dict[str, Any]:
        return self._strategy._build_request(  # type: ignore[union-attr]
            inputs, extra_body=extra_body, streaming=streaming, **parameters
        )

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[AudioParameters],
    ) -> dict[str, Any]:
        return await self._strategy._make_request(  # type: ignore[union-attr]
            request_body, endpoint=endpoint, extra_headers=extra_headers, **parameters
        )

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        return self._strategy._parse_content(response_data)  # type: ignore[union-attr]

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        return self._strategy._parse_usage(response_data)  # type: ignore[union-attr]

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> Any:
        return self._strategy._parse_finish_reason(response_data)  # type: ignore[union-attr]

    def _transform_output(
        self, content: AudioContent, **parameters: Unpack[AudioParameters]
    ) -> AudioContent:
        return self._strategy._transform_output(content, **parameters)  # type: ignore[union-attr]

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        return self._strategy._build_metadata(response_data)  # type: ignore[union-attr]

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[AudioParameters],
    ) -> Any:
        return self._strategy._make_stream_request(  # type: ignore[union-attr]
            request_body, endpoint=endpoint, extra_headers=extra_headers, **parameters
        )

    def _stream_class(self) -> type[AudioStream]:
        return self._strategy._stream_class()  # type: ignore[union-attr]


__all__ = ["ElevenLabsAudioClient"]
