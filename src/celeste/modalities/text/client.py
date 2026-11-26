"""Text modality client."""

from typing import Any, Unpack

from asgiref.sync import async_to_sync

from celeste.client import ModalityClient
from celeste.core import Modality
from celeste.messages import media_types
from celeste.tools import ToolResult, rehydrate_tools
from celeste.types import (
    AudioContent,
    DocumentContent,
    ImageContent,
    Message,
    TextContent,
    VideoContent,
)

from .io import TextChunk, TextFinishReason, TextInput, TextOutput, TextUsage
from .parameters import TextParameters
from .streaming import TextStream


class TextClient(
    ModalityClient[TextInput, TextOutput, TextParameters, TextContent, TextChunk]
):
    """Base text client with generate/analyze operations."""

    modality: Modality = Modality.TEXT
    _usage_class = TextUsage
    _finish_reason_class = TextFinishReason

    @classmethod
    def _output_class(cls) -> type[TextOutput]:
        """Return the Output class for text modality."""
        return TextOutput

    async def generate(
        self,
        prompt: str | None = None,
        *,
        messages: list[Message | ToolResult] | None = None,
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextOutput:
        """Generate text from prompt."""
        self._check_media_support(messages=messages)
        inputs = TextInput(prompt=prompt, messages=messages)
        return await self._predict(
            inputs, extra_body=extra_body, extra_headers=extra_headers, **parameters
        )

    async def analyze(
        self,
        prompt: str | None = None,
        *,
        messages: list[Message | ToolResult] | None = None,
        image: ImageContent | None = None,
        video: VideoContent | None = None,
        audio: AudioContent | None = None,
        document: DocumentContent | None = None,
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextOutput:
        """Analyze image(s), video(s), audio, or document(s) with prompt or messages."""
        self._check_media_support(
            messages=messages,
            image=image,
            video=video,
            audio=audio,
            document=document,
        )
        inputs = TextInput(
            prompt=prompt,
            messages=messages,
            image=image,
            video=video,
            audio=audio,
            document=document,
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
        """Build request, rehydrating serialized tools."""
        tools = parameters.get("tools")
        if isinstance(tools, list):
            parameters["tools"] = rehydrate_tools(tools)
        return super()._build_request(
            inputs, extra_body=extra_body, streaming=streaming, **parameters
        )

    def _check_media_support(
        self,
        image: ImageContent | None = None,
        video: VideoContent | None = None,
        audio: AudioContent | None = None,
        document: DocumentContent | None = None,
        messages: list[Message | ToolResult] | None = None,
    ) -> None:
        """Check model supports the provided media types.

        Raises:
            NotImplementedError: If media type is provided but model doesn't support it.
        """
        provided_media = media_types(
            messages=messages,
            image=image,
            video=video,
            audio=audio,
            document=document,
        )
        for input_type in provided_media:
            if input_type not in self.model.optional_input_types:
                msg = f"Model {self.model.id} does not support {input_type.value} input"
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
        messages: list[Message | ToolResult] | None = None,
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextStream:
        """Stream text generation.

        Usage:
            async for chunk in client.stream.generate("Hello"):
                print(chunk.content)
        """
        self._client._check_media_support(messages=messages)
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
        messages: list[Message | ToolResult] | None = None,
        image: ImageContent | None = None,
        video: VideoContent | None = None,
        audio: AudioContent | None = None,
        document: DocumentContent | None = None,
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextStream:
        """Stream media analysis (image, video, audio, or document).

        Usage:
            async for chunk in client.stream.analyze("Describe", image=img):
                print(chunk.content)

            async for chunk in client.stream.analyze("Summarize", document=doc):
                print(chunk.content)
        """
        self._client._check_media_support(
            messages=messages,
            image=image,
            video=video,
            audio=audio,
            document=document,
        )
        inputs = TextInput(
            prompt=prompt,
            messages=messages,
            image=image,
            video=video,
            audio=audio,
            document=document,
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
        self.generate = async_to_sync(client.generate)
        self.analyze = async_to_sync(client.analyze)

    @property
    def stream(self) -> "TextSyncStreamNamespace":
        """Sync streaming namespace."""
        return TextSyncStreamNamespace(self._client)


TextSyncStreamNamespace = TextStreamNamespace


__all__ = [
    "TextClient",
    "TextStreamNamespace",
    "TextSyncNamespace",
    "TextSyncStreamNamespace",
]
