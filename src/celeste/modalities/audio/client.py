"""Audio modality client."""

from typing import Any, ClassVar, Unpack

from asgiref.sync import async_to_sync

from celeste import telemetry
from celeste.client import ModalityClient
from celeste.core import Modality
from celeste.modalities.text.io import TextFinishReason, TextOutput, TextUsage
from celeste.types import AudioContent

from .io import AudioChunk, AudioFinishReason, AudioInput, AudioOutput, AudioUsage
from .parameters import AudioParameter, AudioParameters
from .streaming import AudioStream


class AudioClient(
    ModalityClient[AudioInput, AudioOutput, AudioParameters, AudioContent, AudioChunk]
):
    """Base audio client with speak, generate, and transcribe operations."""

    modality: Modality = Modality.AUDIO
    _usage_class = AudioUsage
    _finish_reason_class = AudioFinishReason
    _content_fields: ClassVar[set[str]] = {"audio_bytes"}

    _speak_endpoint: ClassVar[str | None] = None
    _generate_endpoint: ClassVar[str | None] = None
    _transcribe_endpoint: ClassVar[str | None] = None

    @classmethod
    def _output_class(cls) -> type[AudioOutput]:
        """Return the Output class for audio modality."""
        return AudioOutput

    async def speak(
        self,
        text: str,
        **parameters: Unpack[AudioParameters],
    ) -> AudioOutput:
        """Convert text to speech audio."""
        inputs = AudioInput(text=text)
        return await self._predict(inputs, endpoint=self._speak_endpoint, **parameters)

    async def generate(
        self,
        prompt: str,
        **parameters: Unpack[AudioParameters],
    ) -> AudioOutput:
        """Generate audio from a prompt."""
        if self._generate_endpoint is None:
            msg = f"Model {self.model.id} does not support audio generation"
            raise NotImplementedError(msg)
        inputs = AudioInput(text=prompt)
        return await self._predict(
            inputs, endpoint=self._generate_endpoint, **parameters
        )

    async def transcribe(
        self,
        audio: AudioContent,
        *,
        prompt: str | None = None,
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[AudioParameters],
    ) -> TextOutput:
        """Transcribe speech audio to text."""
        if self._transcribe_endpoint is None:
            msg = f"Model {self.model.id} does not support audio transcription"
            raise NotImplementedError(msg)
        inputs = AudioInput(audio=audio)
        build_params: dict[str, Any] = dict(parameters)
        if prompt is not None:
            build_params[AudioParameter.PROMPT] = prompt
        with telemetry.gen_ai_span(
            model=self.model,
            provider=self.provider,
            protocol=self.protocol,
            modality=self.modality,
        ) as (span, request_attrs):
            inputs, build_params = self._validate_artifacts(inputs, **build_params)
            telemetry.add_input_event(span, inputs)
            request_body = self._build_request(
                inputs, extra_body=extra_body, **build_params
            )
            response_data = await self._make_request(
                request_body,
                endpoint=self._transcribe_endpoint,
                extra_headers=extra_headers,
            )
            content = self._parse_content(response_data)
            content = self._transform_output(content, **build_params)
            raw_usage = self._parse_usage(response_data)
            finish = self._parse_finish_reason(response_data)
            output = TextOutput(
                content=content,
                usage=TextUsage(**raw_usage),
                finish_reason=TextFinishReason(
                    reason=finish.reason if finish else None
                ),
                metadata=self._build_metadata(response_data),
            )
            telemetry.record_output(span, output, request_attrs)
            return output

    @property
    def stream(self) -> "AudioStreamNamespace":
        """Streaming namespace for audio operations."""
        return AudioStreamNamespace(self)

    @property
    def sync(self) -> "AudioSyncNamespace":
        """Sync namespace for audio operations."""
        return AudioSyncNamespace(self)


class AudioStreamNamespace:
    """Streaming namespace for audio operations."""

    def __init__(self, client: AudioClient) -> None:
        self._client = client

    def speak(
        self,
        text: str,
        *,
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[AudioParameters],
    ) -> AudioStream:
        """Stream speech generation."""
        inputs = AudioInput(text=text)
        return self._client._stream(
            inputs,
            stream_class=self._client._stream_class(),
            extra_body=extra_body,
            extra_headers=extra_headers,
            **parameters,
        )


class AudioSyncNamespace:
    """Sync namespace for audio operations."""

    def __init__(self, client: AudioClient) -> None:
        self._client = client

    def speak(
        self,
        text: str,
        *,
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[AudioParameters],
    ) -> AudioOutput:
        """Blocking speech generation."""
        inputs = AudioInput(text=text)
        return async_to_sync(self._client._predict)(
            inputs, extra_body=extra_body, extra_headers=extra_headers, **parameters
        )

    def generate(
        self,
        prompt: str,
        *,
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[AudioParameters],
    ) -> AudioOutput:
        """Blocking audio generation."""
        if self._client._generate_endpoint is None:
            msg = f"Model {self._client.model.id} does not support audio generation"
            raise NotImplementedError(msg)
        inputs = AudioInput(text=prompt)
        return async_to_sync(self._client._predict)(
            inputs,
            endpoint=self._client._generate_endpoint,
            extra_body=extra_body,
            extra_headers=extra_headers,
            **parameters,
        )

    def transcribe(
        self,
        audio: AudioContent,
        *,
        prompt: str | None = None,
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[AudioParameters],
    ) -> TextOutput:
        """Blocking speech transcription."""
        return async_to_sync(self._client.transcribe)(
            audio,
            prompt=prompt,
            extra_body=extra_body,
            extra_headers=extra_headers,
            **parameters,
        )

    @property
    def stream(self) -> "AudioSyncStreamNamespace":
        """Sync streaming namespace."""
        return AudioSyncStreamNamespace(self._client)


class AudioSyncStreamNamespace:
    """Sync streaming namespace - returns Stream instance with sync iteration support."""

    def __init__(self, client: AudioClient) -> None:
        self._client = client

    def speak(
        self,
        text: str,
        *,
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[AudioParameters],
    ) -> AudioStream:
        """Sync streaming speech generation.

        Returns Stream instance that supports both async and sync iteration.

        Usage:
            stream = client.sync.stream.speak("Hello world")
            for chunk in stream:  # Sync iteration (bridges async internally)
                audio_bytes = chunk.content
            stream.output.content.save("output.mp3")
        """
        # Return same stream as async version - __iter__/__next__ handle sync iteration
        return self._client.stream.speak(
            text, extra_body=extra_body, extra_headers=extra_headers, **parameters
        )


__all__ = [
    "AudioClient",
    "AudioStreamNamespace",
    "AudioSyncNamespace",
    "AudioSyncStreamNamespace",
]
