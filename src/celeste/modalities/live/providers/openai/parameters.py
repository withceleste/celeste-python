"""OpenAI parameter mappers for live."""

from celeste.artifacts import AudioArtifact
from celeste.parameters import ParameterMapper
from celeste.providers.openai.live.parameters import (
    AudioFormatMapper as _AudioFormatMapper,
)
from celeste.providers.openai.live.parameters import (
    ToolsMapper as _ToolsMapper,
)
from celeste.providers.openai.live.parameters import (
    VoiceMapper as _VoiceMapper,
)

from ...parameters import LiveParameter


class VoiceMapper(_VoiceMapper[AudioArtifact]):
    """Map voice to OpenAI Live audio.output.voice."""

    name = LiveParameter.VOICE


class AudioFormatMapper(_AudioFormatMapper[AudioArtifact]):
    """Map audio_format to OpenAI Live audio.format."""

    name = LiveParameter.AUDIO_FORMAT


class ToolsMapper(_ToolsMapper[AudioArtifact]):
    """Map tools to OpenAI Live delegation.responses.tools."""

    name = LiveParameter.TOOLS


OPENAI_PARAMETER_MAPPERS: list[ParameterMapper[AudioArtifact]] = [
    VoiceMapper(),
    AudioFormatMapper(),
    ToolsMapper(),
]

__all__ = ["OPENAI_PARAMETER_MAPPERS"]
