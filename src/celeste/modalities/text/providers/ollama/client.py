"""Ollama text client (OpenResponses protocol)."""

from typing import Any, Unpack

from celeste.modalities.text.providers.openresponses.client import (
    OpenResponsesTextClient,
    OpenResponsesTextStream,
)
from celeste.providers.ollama.responses.config import DEFAULT_BASE_URL
from celeste.types import ImageContent, Message, VideoContent

from ...io import TextInput, TextOutput
from ...parameters import TextParameters
from ...streaming import TextStream


class OllamaTextClient(OpenResponsesTextClient):
    """Ollama - OpenResponses with default localhost:11434."""

    async def generate(
        self,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        base_url: str | None = None,
        extra_body: dict[str, Any] | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextOutput:
        return await super().generate(
            prompt,
            messages=messages,
            base_url=base_url or DEFAULT_BASE_URL,
            extra_body=extra_body,
            **parameters,
        )

    async def analyze(
        self,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        image: ImageContent | None = None,
        video: VideoContent | None = None,
        base_url: str | None = None,
        extra_body: dict[str, Any] | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextOutput:
        return await super().analyze(
            prompt,
            messages=messages,
            image=image,
            video=video,
            base_url=base_url or DEFAULT_BASE_URL,
            extra_body=extra_body,
            **parameters,
        )

    def _stream(
        self,
        inputs: TextInput,
        stream_class: type[TextStream],
        *,
        base_url: str | None = None,
        extra_body: dict[str, Any] | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextStream:
        return super()._stream(
            inputs,
            stream_class,
            base_url=base_url or DEFAULT_BASE_URL,
            extra_body=extra_body,
            **parameters,
        )


OllamaTextStream = OpenResponsesTextStream

__all__ = ["OllamaTextClient", "OllamaTextStream"]
