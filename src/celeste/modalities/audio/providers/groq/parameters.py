"""Groq parameter mappers for audio modality."""

from celeste.parameters import ParameterMapper
from celeste.providers.groq.audio.parameters import (
    LanguageMapper as _LanguageMapper,
)
from celeste.providers.groq.audio.parameters import (
    PromptMapper as _PromptMapper,
)
from celeste.providers.groq.audio.parameters import (
    TemperatureMapper as _TemperatureMapper,
)
from celeste.types import AudioContent

from ...parameters import AudioParameter


class LanguageMapper(_LanguageMapper):
    """Map language to Groq's language parameter."""

    name = AudioParameter.LANGUAGE


class PromptMapper(_PromptMapper):
    """Map prompt to Groq's prompt parameter."""

    name = AudioParameter.PROMPT


class TemperatureMapper(_TemperatureMapper):
    """Map temperature to Groq's temperature parameter."""

    name = AudioParameter.TEMPERATURE


GROQ_PARAMETER_MAPPERS: list[ParameterMapper[AudioContent]] = [
    LanguageMapper(),
    PromptMapper(),
    TemperatureMapper(),
]

__all__ = ["GROQ_PARAMETER_MAPPERS"]
