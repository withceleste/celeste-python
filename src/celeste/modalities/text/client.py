"""Text modality client."""

from typing import Any, Unpack

from asgiref.sync import async_to_sync

from celeste.client import ModalityClient
from celeste.core import InputType, Modality
from celeste.types import AudioContent, ImageContent, Message, TextContent, VideoContent

from .io import TextInput, TextOutput
from .parameters import TextParameters
from .streaming import TextStream


class TextClient(ModalityClient[TextInput, TextOutput, TextParameters, TextContent]):
    """Base text client.

    Providers implement operation methods (generate, analyze).
    """

    modality: Modality = Modality.TEXT

    @classmethod
    def _output_class(cls) -> type[TextOutput]:
        """Return the Output class for text modality."""
        return TextOutput

    def _check_media_support(
        self,
        image: ImageContent | None,
        video: VideoContent | None,
        audio: AudioContent | None,
    ) -> None:
        """Check model supports the provided media types.

        Raises:
            NotImplementedError: If media type is provided but model doesn't support it.
        """
        if image is not None and InputType.IMAGE not in self.model.optional_input_types:
            msg = f"Model {self.model.id} does not support image input"
            raise NotImplementedError(msg)
        if video is not None and InputType.VIDEO not in self.model.optional_input_types:
            msg = f"Model {self.model.id} does not support video input"
            raise NotImplementedError(msg)
        if audio is not None and InputType.AUDIO not in self.model.optional_input_types:
            msg = f"Model {self.model.id} does not support audio input"
            raise NotImplementedError(msg)

    @property
    def stream(self) -> "TextStreamNamespace":
        """Streaming namespace for text operations."""
        return TextStreamNamespace(self)

    @property
    def sync(self) -> "TextSyncNamespace":
        """Sync namespace for text operations."""
        return TextSyncNamespace(self)


class TextStreamNamespace:
    """Streaming namespace for text operations.

    Provides `client.stream.generate()` and `client.stream.analyze()`.
    """

    def __init__(self, client: TextClient) -> None:
        self._client = client

    def generate(
        self,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        base_url: str | None = None,
        extra_body: dict[str, Any] | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextStream:
        """Stream text generation.

        Usage:
            async for chunk in client.stream.generate("Hello"):
                print(chunk.content)
        """
        inputs = TextInput(prompt=prompt, messages=messages)
        return self._client._stream(
            inputs,
            stream_class=self._client._stream_class(),
            base_url=base_url,
            extra_body=extra_body,
            **parameters,
        )

    def analyze(
        self,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        image: ImageContent | None = None,
        video: VideoContent | None = None,
        audio: AudioContent | None = None,
        base_url: str | None = None,
        extra_body: dict[str, Any] | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextStream:
        """Stream media analysis (image, video, or audio).

        Usage:
            async for chunk in client.stream.analyze("Describe", image=img):
                print(chunk.content)

            async for chunk in client.stream.analyze("Describe", video=vid):
                print(chunk.content)

            async for chunk in client.stream.analyze("Transcribe", audio=aud):
                print(chunk.content)
        """
        if messages is None:
            self._client._check_media_support(image=image, video=video, audio=audio)
        inputs = TextInput(
            prompt=prompt, messages=messages, image=image, video=video, audio=audio
        )
        return self._client._stream(
            inputs,
            stream_class=self._client._stream_class(),
            base_url=base_url,
            extra_body=extra_body,
            **parameters,
        )


class TextSyncNamespace:
    """Sync namespace for text operations.

    Provides `client.sync.generate()` and `client.sync.analyze()`.
    """

    def __init__(self, client: TextClient) -> None:
        self._client = client

    def generate(
        self,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        base_url: str | None = None,
        extra_body: dict[str, Any] | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextOutput:
        """Blocking text generation.

        Usage:
            result = client.sync.generate("Hello")
            print(result.content)
        """
        inputs = TextInput(prompt=prompt, messages=messages)
        return async_to_sync(self._client._predict)(
            inputs, base_url=base_url, extra_body=extra_body, **parameters
        )

    def analyze(
        self,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        image: ImageContent | None = None,
        video: VideoContent | None = None,
        audio: AudioContent | None = None,
        base_url: str | None = None,
        extra_body: dict[str, Any] | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextOutput:
        """Blocking media analysis (image, video, or audio).

        Usage:
            result = client.sync.analyze("Describe", image=img)
            print(result.content)

            result = client.sync.analyze("Describe", video=vid)
            print(result.content)

            result = client.sync.analyze("Transcribe", audio=aud)
            print(result.content)
        """
        if messages is None:
            self._client._check_media_support(image=image, video=video, audio=audio)
        inputs = TextInput(
            prompt=prompt, messages=messages, image=image, video=video, audio=audio
        )
        return async_to_sync(self._client._predict)(
            inputs, base_url=base_url, extra_body=extra_body, **parameters
        )

    @property
    def stream(self) -> "TextSyncStreamNamespace":
        """Sync streaming namespace."""
        return TextSyncStreamNamespace(self._client)


class TextSyncStreamNamespace:
    """Sync streaming namespace - returns Stream instance with sync iteration support."""

    def __init__(self, client: TextClient) -> None:
        self._client = client

    def generate(
        self,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        base_url: str | None = None,
        extra_body: dict[str, Any] | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextStream:
        """Sync streaming text generation.

        Returns Stream instance that supports both async and sync iteration.

        Usage:
            stream = client.sync.stream.generate("Hello")
            for chunk in stream:  # Sync iteration (bridges async internally)
                print(chunk.content, end="")
            print(stream.output.usage)
        """
        # Return same stream as async version - __iter__/__next__ handle sync iteration
        return self._client.stream.generate(
            prompt,
            messages=messages,
            base_url=base_url,
            extra_body=extra_body,
            **parameters,
        )

    def analyze(
        self,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        image: ImageContent | None = None,
        video: VideoContent | None = None,
        audio: AudioContent | None = None,
        base_url: str | None = None,
        extra_body: dict[str, Any] | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextStream:
        """Sync streaming media analysis (image, video, or audio).

        Returns Stream instance that supports both async and sync iteration.

        Usage:
            stream = client.sync.stream.analyze("Describe", image=img)
            for chunk in stream:  # Sync iteration (bridges async internally)
                print(chunk.content, end="")
            print(stream.output.usage)

            stream = client.sync.stream.analyze("Describe", video=vid)
            for chunk in stream:
                print(chunk.content, end="")
            print(stream.output.usage)

            stream = client.sync.stream.analyze("Transcribe", audio=aud)
            for chunk in stream:
                print(chunk.content, end="")
            print(stream.output.usage)
        """
        # Return same stream as async version - __iter__/__next__ handle sync iteration
        return self._client.stream.analyze(
            prompt,
            messages=messages,
            image=image,
            video=video,
            audio=audio,
            base_url=base_url,
            extra_body=extra_body,
            **parameters,
        )


__all__ = [
    "TextClient",
    "TextStreamNamespace",
    "TextSyncNamespace",
    "TextSyncStreamNamespace",
]
