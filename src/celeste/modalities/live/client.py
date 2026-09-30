"""Live modality client."""

from typing import Any, Unpack

from celeste.artifacts import AudioArtifact
from celeste.client import ModalityClient
from celeste.core import Modality
from celeste.messages import media_types
from celeste.tools import ToolResult, rehydrate_tools
from celeste.types import Message

from .io import LiveChunk, LiveFinishReason, LiveInput, LiveOutput, LiveUsage
from .parameters import LiveParameters
from .streaming import LiveStream


class LiveClient(
    ModalityClient[LiveInput, LiveOutput, LiveParameters, AudioArtifact, LiveChunk]
):
    """Base live client with connect operation."""

    modality: Modality = Modality.LIVE
    _usage_class = LiveUsage
    _finish_reason_class = LiveFinishReason

    @classmethod
    def _output_class(cls) -> type[LiveOutput]:
        """Return the Output class for live modality."""
        return LiveOutput

    def connect(
        self,
        *,
        messages: list[Message | ToolResult] | None = None,
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[LiveParameters],
    ) -> LiveStream:
        """Open a livestream.

        Usage:
            async with client.connect(voice="Kore") as livestream:
                await livestream.send("Hello")
                async for chunk in livestream:
                    play(chunk.content)
        """
        self._check_media_support(messages=messages)
        inputs = LiveInput(messages=messages)
        return self._stream(
            inputs,
            stream_class=self._stream_class(),
            extra_body=extra_body,
            extra_headers=extra_headers,
            **parameters,
        )

    def _build_request(
        self,
        inputs: LiveInput,
        extra_body: dict[str, Any] | None = None,
        streaming: bool = False,
        **parameters: Unpack[LiveParameters],
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
        messages: list[Message | ToolResult] | None = None,
    ) -> None:
        """Check model supports the media types in the seed messages.

        Raises:
            NotImplementedError: If media type is provided but model doesn't support it.
        """
        for input_type in media_types(messages=messages):
            if input_type not in self.model.optional_input_types:
                msg = f"Model {self.model.id} does not support {input_type.value} input"
                raise NotImplementedError(msg)


__all__ = ["LiveClient"]
