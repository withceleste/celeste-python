from typing import Any

import pytest

from celeste.artifacts import ImageArtifact
from celeste.constraints import Dimensions
from celeste.core import Modality, Operation, Provider
from celeste.exceptions import ConstraintViolationError
from celeste.mime_types import ImageMimeType
from celeste.modalities.images.io import ImageInput
from celeste.modalities.images.parameters import ImageParameter as IP
from celeste.modalities.images.providers.bfl.client import BFLImagesClient
from celeste.models import get_model

FLUX_2 = [
    "flux-2-max",
    "flux-2-pro",
    "flux-2-pro-preview",
    "flux-2-flex",
    "flux-2-klein-4b",
    "flux-2-klein-9b",
    "flux-2-klein-9b-preview",
]
LEGACY_DIMENSIONS = ["flux-pro-1.1", "flux-dev"]
PRIMARY = ImageArtifact(data=b"primary", mime_type=ImageMimeType.PNG)
REFERENCE = ImageArtifact(url="https://example.com/reference.png")


@pytest.mark.parametrize(
    ("model_id", "size", "size_fields", "upsampling_field", "editable"),
    [
        ("flux-2-max", "4096x512", {"width": 4096, "height": 512}, "disable_pup", True),
        ("flux-2-pro", "4096x512", {"width": 4096, "height": 512}, "disable_pup", True),
        (
            "flux-2-pro-preview",
            "4096x512",
            {"width": 4096, "height": 512},
            "disable_pup",
            True,
        ),
        (
            "flux-2-flex",
            "4096x512",
            {"width": 4096, "height": 512},
            "prompt_upsampling",
            True,
        ),
        ("flux-2-klein-4b", "4096x512", {"width": 4096, "height": 512}, None, True),
        ("flux-2-klein-9b", "4096x512", {"width": 4096, "height": 512}, None, True),
        (
            "flux-2-klein-9b-preview",
            "4096x512",
            {"width": 4096, "height": 512},
            None,
            True,
        ),
        (
            "flux-kontext-pro",
            "16:9",
            {"aspect_ratio": "16:9"},
            "prompt_upsampling",
            True,
        ),
        (
            "flux-kontext-max",
            "16:9",
            {"aspect_ratio": "16:9"},
            "prompt_upsampling",
            True,
        ),
        (
            "flux-pro-1.1-ultra",
            "16:9",
            {"aspect_ratio": "16:9"},
            "prompt_upsampling",
            False,
        ),
        (
            "flux-pro-1.1",
            "1440x256",
            {"width": 1440, "height": 256},
            "prompt_upsampling",
            False,
        ),
        (
            "flux-dev",
            "1440x256",
            {"width": 1440, "height": 256},
            "prompt_upsampling",
            False,
        ),
    ],
)
@pytest.mark.parametrize("upsampling", [False, True, None])
def test_bfl_family_requests(
    model_id: str,
    size: str,
    size_fields: dict[str, Any],
    upsampling_field: str | None,
    editable: bool,
    upsampling: bool | None,
) -> None:
    model = get_model(model_id, Provider.BFL)
    assert model is not None
    operations = (
        {Operation.GENERATE, Operation.EDIT} if editable else {Operation.GENERATE}
    )
    assert model.operations == {Modality.IMAGES: operations}
    assert not model.streaming
    assert (IP.PROMPT_UPSAMPLING in model.supported_parameters) == (
        upsampling_field is not None
    )
    assert {
        IP.ASPECT_RATIO,
        IP.SEED,
        IP.SAFETY_TOLERANCE,
        IP.OUTPUT_FORMAT,
    } <= model.supported_parameters
    assert (IP.REFERENCE_IMAGES in model.supported_parameters) == editable
    client = BFLImagesClient.model_construct(model=model, provider=Provider.BFL)

    for image in [None, PRIMARY] if editable else [None]:
        parameters: dict[str, Any] = {
            "aspect_ratio": size,
            "prompt_upsampling": upsampling,
            "seed": 0,
            "safety_tolerance": 0,
            "output_format": "webp",
        }
        expected = {
            "prompt": "A red apple",
            "seed": 0,
            "safety_tolerance": 0,
            "output_format": "webp",
            **size_fields,
        }
        if upsampling_field is not None and upsampling is not None:
            expected[upsampling_field] = (
                not upsampling if upsampling_field == "disable_pup" else upsampling
            )
        if image is not None:
            expected["input_image"] = "cHJpbWFyeQ=="
        if editable:
            parameters["reference_images"] = [REFERENCE]
            expected["input_image_2" if image else "input_image"] = REFERENCE.url
        assert (
            client._build_request(
                ImageInput(prompt="A red apple", image=image), **parameters
            )
            == expected
        )


@pytest.mark.parametrize("model_id", FLUX_2 + LEGACY_DIMENSIONS)
def test_bfl_pixel_dimensions_are_exact(model_id: str) -> None:
    model = get_model(model_id, Provider.BFL)
    assert model is not None
    constraint = model.parameter_constraints[IP.ASPECT_RATIO]
    assert isinstance(constraint, Dimensions)
    client = BFLImagesClient.model_construct(model=model, provider=Provider.BFL)
    if model_id in FLUX_2:
        valid = ["64x64", "64x4096", "4096x64", "2048x2048"]
        invalid = ["48x128", "128x48", "1920x1080", "1080x1920", "2064x2048"]
    else:
        valid = ["256x256", "256x1440", "1440x256", "1440x1440"]
        invalid = ["224x512", "512x224", "1472x1024", "1024x1472", "272x512", "512x272"]
    for value in valid:
        width, height = map(int, value.split("x"))
        assert client._build_request(
            ImageInput(prompt="A red apple"), aspect_ratio=value
        ) == {"prompt": "A red apple", "width": width, "height": height}
    for value in invalid:
        with pytest.raises(ConstraintViolationError):
            client._build_request(ImageInput(prompt="A red apple"), aspect_ratio=value)
    for name, dimensions in (constraint.presets or {}).items():
        width, height = map(int, dimensions.split("x"))
        assert client._build_request(
            ImageInput(prompt="A red apple"), aspect_ratio=name
        ) == {"prompt": "A red apple", "width": width, "height": height}


@pytest.mark.parametrize("model_id", ["flux-kontext-pro", "flux-kontext-max"])
def test_kontext_preserves_order_with_three_additional_images(model_id: str) -> None:
    model = get_model(model_id, Provider.BFL)
    assert model is not None
    client = BFLImagesClient.model_construct(model=model, provider=Provider.BFL)
    references = [ImageArtifact(url=f"https://example.com/{i}.png") for i in range(3)]
    request = client._build_request(
        ImageInput(prompt="Compose these", image=PRIMARY), reference_images=references
    )
    assert request == {
        "prompt": "Compose these",
        "input_image": "cHJpbWFyeQ==",
        "input_image_2": references[0].url,
        "input_image_3": references[1].url,
        "input_image_4": references[2].url,
    }
    with pytest.raises(ConstraintViolationError):
        client._build_request(
            ImageInput(prompt="Compose these", image=PRIMARY),
            reference_images=[*references, REFERENCE],
        )


@pytest.mark.parametrize(
    "model_id",
    [
        *FLUX_2,
        "flux-kontext-pro",
        "flux-kontext-max",
        "flux-pro-1.1-ultra",
        *LEGACY_DIMENSIONS,
    ],
)
def test_bfl_integer_controls_and_family_limits(model_id: str) -> None:
    model = get_model(model_id, Provider.BFL)
    assert model is not None
    constraint = model.parameter_constraints[IP.SAFETY_TOLERANCE]
    maximum = 5 if model_id in FLUX_2 else 6
    assert constraint(maximum) == maximum
    for invalid in [-1, 0.5, maximum + 1]:
        with pytest.raises(ConstraintViolationError):
            constraint(invalid)
    if model_id in {"flux-dev", "flux-2-flex"}:
        assert model.parameter_constraints[IP.STEPS](50) == 50
        for invalid in [0, 1.5, 51]:
            with pytest.raises(ConstraintViolationError):
                model.parameter_constraints[IP.STEPS](invalid)
        guidance_max = 5 if model_id == "flux-dev" else 10
        assert model.parameter_constraints[IP.GUIDANCE](guidance_max) == guidance_max
        with pytest.raises(ConstraintViolationError):
            model.parameter_constraints[IP.GUIDANCE](guidance_max + 0.1)
