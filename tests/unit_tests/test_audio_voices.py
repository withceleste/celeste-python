import pytest

from celeste.core import Modality, Operation, Provider
from celeste.modalities.audio.constraints import VoiceConstraint
from celeste.modalities.audio.parameters import AudioParameter
from celeste.modalities.audio.providers.elevenlabs.voices import ELEVENLABS_VOICES
from celeste.modalities.audio.providers.google.models import (
    MODELS as GOOGLE_AUDIO_MODELS,
)
from celeste.modalities.audio.providers.google.voices import GOOGLE_VOICES
from celeste.modalities.audio.providers.gradium.voices import GRADIUM_VOICES
from celeste.modalities.audio.providers.openai.voices import OPENAI_VOICES
from celeste.modalities.audio.voices import Voice


def test_voice_description_defaults_to_none() -> None:
    voice = Voice(id="voice-id", provider=Provider.OPENAI, name="Voice")

    assert voice.description is None


@pytest.mark.parametrize(
    ("voices", "expected_count"),
    [
        (GRADIUM_VOICES, 66),
        (ELEVENLABS_VOICES, 21),
        (GOOGLE_VOICES, 30),
        (OPENAI_VOICES, 13),
    ],
)
def test_voice_catalogs_are_complete_and_unique(
    voices: list[Voice], expected_count: int
) -> None:
    assert len(voices) == expected_count
    assert len({voice.id for voice in voices}) == expected_count
    assert len({voice.name for voice in voices}) == expected_count


def test_provider_descriptions_match_published_metadata() -> None:
    assert all(voice.description for voice in GRADIUM_VOICES)
    assert all(voice.description for voice in ELEVENLABS_VOICES)
    assert all(voice.description for voice in GOOGLE_VOICES)
    assert all(voice.description is None for voice in OPENAI_VOICES)

    assert GRADIUM_VOICES[0].description == (
        "Playful, upbeat and Gen Z energy voice with a standard American accent. "
        "Perfect for engaging conversations!"
    )
    assert GOOGLE_VOICES[0].name == "Zephyr"
    assert GOOGLE_VOICES[0].description == "Bright"


def test_google_generate_audio_models_reject_output_format() -> None:
    """output_format is SPEAK-only: Google's Lyria (GENERATE) endpoint rejects
    response_format.mime_type, so GENERATE audio models must not declare it."""
    generate_models = [
        m
        for m in GOOGLE_AUDIO_MODELS
        if Operation.GENERATE in m.operations.get(Modality.AUDIO, set())
    ]
    assert generate_models
    assert all(
        AudioParameter.OUTPUT_FORMAT not in m.parameter_constraints
        for m in generate_models
    )


def test_voice_constraint_still_accepts_name_and_id() -> None:
    voice = GRADIUM_VOICES[0]
    constraint = VoiceConstraint(voices=GRADIUM_VOICES)

    assert constraint(voice.name) == voice.id
    assert constraint(voice.id) == voice.id
