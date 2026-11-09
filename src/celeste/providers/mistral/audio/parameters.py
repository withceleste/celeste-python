"""Mistral Audio API parameter mappers."""

from celeste.parameters import FieldMapper


class LanguageMapper[Content](FieldMapper[Content]):
    """Map language to Mistral language field."""

    field = "language"


class TemperatureMapper[Content](FieldMapper[Content]):
    """Map temperature to Mistral temperature field."""

    field = "temperature"


__all__ = [
    "LanguageMapper",
    "TemperatureMapper",
]
