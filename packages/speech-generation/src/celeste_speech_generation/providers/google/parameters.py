"""Google parameter mappers for speech generation."""

from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste_speech_generation.parameters import SpeechGenerationParameter


class VoiceMapper(ParameterMapper):
    """Map voice parameter to Google speechConfig.voiceConfig.prebuiltVoiceConfig.voiceName."""

    name = SpeechGenerationParameter.VOICE

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform voice into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request.setdefault("generationConfig", {}).setdefault(
            "speechConfig", {}
        ).setdefault("voiceConfig", {}).setdefault("prebuiltVoiceConfig", {})[
            "voiceName"
        ] = validated_value
        return request


class PromptMapper(ParameterMapper):
    """Map prompt parameter to style instructions in text."""

    name = SpeechGenerationParameter.PROMPT

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Prepend prompt as style instruction to text using SSML-like tags."""
        if not value or not isinstance(value, str):
            return request

        contents = request.get("contents", [])
        if contents and contents[0].get("parts"):
            text = contents[0]["parts"][0].get("text", "")
            contents[0]["parts"][0]["text"] = (
                f"<style instruction='{value}'>{text}</style>"
            )

        return request


GOOGLE_PARAMETER_MAPPERS: list[ParameterMapper] = [
    VoiceMapper(),
    PromptMapper(),
]

__all__ = ["GOOGLE_PARAMETER_MAPPERS"]
