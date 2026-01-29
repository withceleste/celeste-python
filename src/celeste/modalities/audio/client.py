"""Audio modality client."""

from typing import Any, Unpack

from asgiref.sync import async_to_sync

from celeste.client import ModalityClient
from celeste.core import Modality
from celeste.types import AudioContent

from .io import AudioInput, AudioOutput
from .parameters import AudioParameters
from .streaming import AudioStream


class AudioClient(
    ModalityClient[AudioInput, AudioOutput, AudioParameters, AudioContent]
):
    """Base audio client. Providers implement speak() method."""

    modality: Modality = Modality.AUDIO

    @classmethod
    def _output_class(cls) -> type[AudioOutput]:
        """Return the Output class for audio modality."""
        return AudioOutput

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
        **parameters: Unpack[AudioParameters],
    ) -> AudioStream:
        """Stream speech generation."""
        inputs = AudioInput(text=text)
        return self._client._stream(
            inputs,
            stream_class=self._client._stream_class(),
            extra_body=extra_body,
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
        **parameters: Unpack[AudioParameters],
    ) -> AudioOutput:
        """Blocking speech generation."""
        inputs = AudioInput(text=text)
        return async_to_sync(self._client._predict)(
            inputs, extra_body=extra_body, **parameters
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
        return self._client.stream.speak(text, extra_body=extra_body, **parameters)


__all__ = [
    "AudioClient",
    "AudioStreamNamespace",
    "AudioSyncNamespace",
    "AudioSyncStreamNamespace",
]
