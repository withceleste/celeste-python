"""Google parameter mappers for live."""

from celeste.artifacts import AudioArtifact
from celeste.parameters import ParameterMapper
from celeste.providers.google.live.parameters import (
    MaxOutputTokensMapper as _MaxOutputTokensMapper,
    MediaContentMapper as _MediaContentMapper,
    SeedMapper as _SeedMapper,
    TemperatureMapper as _TemperatureMapper,
    ThinkingLevelMapper as _ThinkingLevelMapper,
    ToolsMapper as _ToolsMapper,
    VoiceNameMapper as _VoiceNameMapper,
)

from ...parameters import LiveParameter


class VoiceMapper(_VoiceNameMapper[AudioArtifact]):
    """Map voice to Google Live voiceName."""

    name = LiveParameter.VOICE


class ReferenceImagesMapper(_MediaContentMapper[AudioArtifact]):
    """Map reference_images to Google Live seeded client content."""

    name = LiveParameter.REFERENCE_IMAGES


class ThinkingLevelMapper(_ThinkingLevelMapper[AudioArtifact]):
    """Map thinking_level to Google Live thinkingLevel."""

    name = LiveParameter.THINKING_LEVEL


class ToolsMapper(_ToolsMapper[AudioArtifact]):
    """Map tools to Google Live tool declarations."""

    name = LiveParameter.TOOLS


class TemperatureMapper(_TemperatureMapper[AudioArtifact]):
    """Map temperature to Google Live temperature."""

    name = LiveParameter.TEMPERATURE


class MaxTokensMapper(_MaxOutputTokensMapper[AudioArtifact]):
    """Map max_tokens to Google Live maxOutputTokens."""

    name = LiveParameter.MAX_TOKENS


class SeedMapper(_SeedMapper[AudioArtifact]):
    """Map seed to Google Live seed."""

    name = LiveParameter.SEED


GOOGLE_PARAMETER_MAPPERS: list[ParameterMapper[AudioArtifact]] = [
    VoiceMapper(),
    ReferenceImagesMapper(),
    ThinkingLevelMapper(),
    ToolsMapper(),
    TemperatureMapper(),
    MaxTokensMapper(),
    SeedMapper(),
]

__all__ = ["GOOGLE_PARAMETER_MAPPERS"]
