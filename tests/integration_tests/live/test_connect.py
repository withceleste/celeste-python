"""Bounded livestreams; require provider credentials and incur API usage."""

import asyncio
import io
import wave

import pytest

import celeste
from celeste.artifacts import AudioArtifact, ImageArtifact
from celeste.mime_types import AudioMimeType
from celeste.types import ImagePart, Message, Role, TextPart


def spoken(messages: list, role: Role) -> str:
    return "".join(
        m.content
        for m in messages
        if isinstance(m, Message) and m.role == role and isinstance(m.content, str)
    )


@pytest.mark.parametrize(
    "model", ["gemini-3.8-live", "gemini-3.8-live-extended-thinking"]
)
async def test_google_livestream(model: str) -> None:
    async with (
        asyncio.timeout(60),
        celeste.live.connect(
            model=model,
            **(
                {"thinking_level": "LOW"} if model.endswith("extended-thinking") else {}
            ),
        ) as livestream,
    ):
        await livestream.send("Say hello in one short sentence.")
        async for chunk in livestream:
            if chunk.finish_reason:
                await livestream.end()
    output = livestream.output
    assert output.content.data
    assert output.content.mime_type == AudioMimeType.PCM
    assert output.content.metadata["sample_rate"] == 24000
    assert output.usage.total_tokens
    assert spoken(output.messages, Role.ASSISTANT)


@pytest.mark.parametrize("seed", [False, True])
async def test_google_livestream_image_question(
    square_image: ImageArtifact, seed: bool
) -> None:
    question = "What color is the shape in the picture? Answer briefly in English."
    async with (
        asyncio.timeout(60),
        celeste.live.connect(
            model="gemini-3.8-live", reference_images=[square_image] if seed else []
        ) as livestream,
    ):
        await livestream.send(
            question
            if seed
            else Message(
                role=Role.USER,
                content=[ImagePart(image=square_image), TextPart(text=question)],
            )
        )
        async for chunk in livestream:
            if chunk.finish_reason:
                await livestream.end()
    assert "red" in spoken(livestream.output.messages, Role.ASSISTANT).lower()


async def test_openai_livestream() -> None:
    speech = await celeste.audio.speak(
        "Hello. Please say hello back.",
        model="gpt-4o-mini-tts",
        voice="alloy",
        output_format=AudioMimeType.WAV,
    )
    with wave.open(io.BytesIO(speech.content.get_bytes()), "rb") as wav:
        assert (wav.getnchannels(), wav.getsampwidth(), wav.getframerate()) == (
            1,
            2,
            24000,
        )
        pcm = wav.readframes(wav.getnframes())
    # One second of trailing silence lets server-side turn detection fire.
    pcm += bytes(48000)
    async with (
        asyncio.timeout(60),
        celeste.live.connect(model="gpt-live-1") as livestream,
    ):
        for start in range(0, len(pcm), 960):
            await livestream.send(
                AudioArtifact(
                    data=pcm[start : start + 960], mime_type=AudioMimeType.PCM
                )
            )
        async for chunk in livestream:
            if chunk.transcript and chunk.transcript.role == Role.ASSISTANT:
                await livestream.end()
    output = livestream.output
    assert output.content.data
    assert output.usage.billed_units is not None
    assert output.finish_reason is not None
    assert output.finish_reason.reason == "close_requested"
