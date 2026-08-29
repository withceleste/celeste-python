"""Unit tests for Google image model metadata."""

from celeste.constraints import Choice
from celeste.modalities.images.parameters import ImageParameter
from celeste.modalities.images.providers.google.models import GOOGLE_GEMINI_MODELS


def test_flash_lite_supports_all_documented_aspect_ratios() -> None:
    model = next(
        model
        for model in GOOGLE_GEMINI_MODELS
        if model.id == "gemini-3.1-flash-lite-image"
    )
    constraint = model.parameter_constraints[ImageParameter.ASPECT_RATIO]

    assert isinstance(constraint, Choice)
    assert constraint.options == [
        "1:1",
        "1:4",
        "1:8",
        "2:3",
        "3:2",
        "3:4",
        "4:1",
        "4:3",
        "4:5",
        "5:4",
        "8:1",
        "9:16",
        "16:9",
        "21:9",
    ]
