"""Parameter mappers for Gradium audio recognition."""

from typing import Any

from celeste import Model
from celeste.parameters import ParameterMapper
from celeste_audio_recognition.parameters import AudioRecognitionParameter


class InputFormatMapper(ParameterMapper):
    """Map input_format parameter to Gradium input_format field."""

    name = AudioRecognitionParameter.INPUT_FORMAT

    def map(self, request: dict[str, Any], value: object, model: Model) -> dict[str, Any]:
        """Map input_format to Gradium format."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["input_format"] = validated_value
        return request


# List of all Gradium parameter mappers
GRADIUM_PARAMETER_MAPPERS: list[ParameterMapper] = [
    InputFormatMapper(),
]

__all__ = [
    "GRADIUM_PARAMETER_MAPPERS",
    "InputFormatMapper",
]
