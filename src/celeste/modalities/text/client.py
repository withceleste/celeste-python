"""Text modality client."""

import warnings
from typing import Any, ClassVar, Unpack

from asgiref.sync import async_to_sync

from celeste.client import ModalityClient
from celeste.core import InputType, Modality
from celeste.tools import CodeExecution, WebSearch, XSearch
from celeste.types import AudioContent, ImageContent, Message, TextContent, VideoContent

from .io import TextChunk, TextFinishReason, TextInput, TextOutput, TextUsage
from .parameters import TextParameters
from .streaming import TextStream


class TextClient(
    ModalityClient[TextInput, TextOutput, TextParameters, TextContent, TextChunk]
):
    """Base text client.

    Provides default ``generate()`` and ``analyze()`` operations.
    """

    modality: Modality = Modality.TEXT
    _usage_class = TextUsage
    _finish_reason_class = TextFinishReason

    # Deprecated param → Tool class mapping.
    # TODO(deprecation): Remove on 2026-06-07.
    _DEPRECATED_TOOL_PARAMS: ClassVar[dict[str, type]] = {
        "web_search": WebSearch,
        "x_search": XSearch,
        "code_execution": CodeExecution,
    }

    @classmethod
    def _output_class(cls) -> type[TextOutput]:
        """Return the Output class for text modality."""
        return TextOutput

    async def generate(
        self,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextOutput:
        """Generate text from prompt."""
        inputs = TextInput(prompt=prompt, messages=messages)
        return await self._predict(
            inputs, extra_body=extra_body, extra_headers=extra_headers, **parameters
        )

    async def analyze(
        self,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        image: ImageContent | None = None,
        video: VideoContent | None = None,
        audio: AudioContent | None = None,
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextOutput:
        """Analyze image(s), video(s), or audio with prompt or messages."""
        if messages is None:
            self._check_media_support(image=image, video=video, audio=audio)
        inputs = TextInput(
            prompt=prompt, messages=messages, image=image, video=video, audio=audio
        )
        return await self._predict(
            inputs, extra_body=extra_body, extra_headers=extra_headers, **parameters
        )

    def _build_request(
        self,
        inputs: TextInput,
        extra_body: dict[str, Any] | None = None,
        streaming: bool = False,
        **parameters: Unpack[TextParameters],
    ) -> dict[str, Any]:
        """Build request, migrating deprecated boolean tool params first.

        TODO(deprecation): Remove this override on 2026-06-07.
        """
        for old_param, tool_cls in self._DEPRECATED_TOOL_PARAMS.items():
            value = parameters.pop(old_param, None)  # type: ignore[misc]
            if value:
                warnings.warn(
                    f"'{old_param}=True' is deprecated, "
                    f"use tools=[{tool_cls.__name__}()] instead. "
                    "Will be removed on 2026-06-07.",
                    DeprecationWarning,
                    stacklevel=4,
                )
                parameters.setdefault("tools", []).append(tool_cls())
        return super()._build_request(
            inputs, extra_body=extra_body, streaming=streaming, **parameters
        )

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
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
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
            extra_body=extra_body,
            extra_headers=extra_headers,
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
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
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
            extra_body=extra_body,
            extra_headers=extra_headers,
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
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextOutput:
        """Blocking text generation.

        Usage:
            result = client.sync.generate("Hello")
            print(result.content)
        """
        inputs = TextInput(prompt=prompt, messages=messages)
        return async_to_sync(self._client._predict)(
            inputs,
            extra_body=extra_body,
            extra_headers=extra_headers,
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
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
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
            inputs,
            extra_body=extra_body,
            extra_headers=extra_headers,
            **parameters,
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
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
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
            extra_body=extra_body,
            extra_headers=extra_headers,
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
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
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
            extra_body=extra_body,
            extra_headers=extra_headers,
            **parameters,
        )


__all__ = [
    "TextClient",
    "TextStreamNamespace",
    "TextSyncNamespace",
    "TextSyncStreamNamespace",
]
