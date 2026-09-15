"""Binary audio is serialized once while finish metadata remains available."""

from collections.abc import AsyncIterator
from typing import Any

import pytest

from celeste.modalities.audio.providers.elevenlabs.text_to_speech import (
    ElevenLabsTextToSpeechAudioStream,
)
from celeste.modalities.audio.providers.gradium.client import GradiumAudioStream


@pytest.mark.parametrize(
    "stream_class", [ElevenLabsTextToSpeechAudioStream, GradiumAudioStream]
)
async def test_audio_metadata_excludes_binary_chunks(stream_class: type) -> None:
    data = bytes([255, 254, 0, 1]) * 16384

    async def events() -> AsyncIterator[dict[str, Any]]:
        yield {"data": data}
        yield {"finish_reason": "stop"}

    stream = stream_class(events())
    _ = [chunk async for chunk in stream]
    output = stream.output
    assert output.content.data == data
    assert (
        len(output.model_dump_json())
        < len(output.model_dump_json(exclude={"metadata"})) + 1024
    )
    if stream_class is GradiumAudioStream:
        assert output.metadata["raw_events"] == [{"finish_reason": "stop"}]
        assert output.finish_reason.reason == "stop"
    else:
        assert output.metadata["raw_events"] == []
