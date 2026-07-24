"""Mistral parameter mappers for audio modality."""

from celeste.parameters import ParameterMapper
from celeste.providers.mistral.audio.parameters import (
    LanguageMapper as _LanguageMapper,
)
from celeste.providers.mistral.audio.parameters import (
    TemperatureMapper as _TemperatureMapper,
)
from celeste.types import AudioContent

from ...parameters import AudioParameter


class LanguageMapper(_LanguageMapper):
    """Map language to Mistral's language parameter."""

    name = AudioParameter.LANGUAGE


class TemperatureMapper(_TemperatureMapper):
    """Map temperature to Mistral's temperature parameter."""

    name = AudioParameter.TEMPERATURE


MISTRAL_PARAMETER_MAPPERS: list[ParameterMapper[AudioContent]] = [
    LanguageMapper(),
    TemperatureMapper(),
]

__all__ = ["MISTRAL_PARAMETER_MAPPERS"]
