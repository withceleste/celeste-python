"""Unit tests for Google images provider Interactions/Vertex dispatch and wire shape."""

import pytest
from pydantic import SecretStr

from celeste import Model, create_client
from celeste.artifacts import ImageArtifact
from celeste.auth import AuthHeader
from celeste.constraints import ImagesConstraint
from celeste.core import Modality, Operation, Provider
from celeste.exceptions import ConstraintViolationError
from celeste.mime_types import ImageMimeType
from celeste.modalities.images.io import ImageInput
from celeste.modalities.images.parameters import ImageParameter
from celeste.modalities.images.providers.google.client import GoogleImagesClient
from celeste.modalities.images.providers.google.interactions import (
    GoogleInteractionsImagesClient,
)
from celeste.modalities.images.providers.google.vertex import GoogleVertexImagesClient
from celeste.providers.google.auth import GoogleADC


def _model() -> Model:
    return Model(
        id="gemini-3.1-flash-image",
        provider=Provider.GOOGLE,
        display_name="Nano Banana 2",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
    )


def _api_key_auth() -> AuthHeader:
    return AuthHeader(secret=SecretStr("test"), header="x-goog-api-key", prefix="")


def test_api_key_auth_dispatches_to_interactions_strategy() -> None:
    client = GoogleImagesClient(
        model=_model(), provider=Provider.GOOGLE, auth=_api_key_auth()
    )
    assert isinstance(client._strategy, GoogleInteractionsImagesClient)
    assert client._generate_endpoint == client._strategy._generate_endpoint
    assert client._edit_endpoint == client._strategy._edit_endpoint


def test_google_adc_auth_dispatches_to_vertex_strategy() -> None:
    client = GoogleImagesClient(
        model=_model(), provider=Provider.GOOGLE, auth=GoogleADC(project_id="p")
    )
    assert isinstance(client._strategy, GoogleVertexImagesClient)
    assert client._generate_endpoint == client._strategy._generate_endpoint
    assert client._edit_endpoint == client._strategy._edit_endpoint


@pytest.mark.parametrize("use_adc", [False, True], ids=["api-key", "adc"])
@pytest.mark.parametrize(
    ("primary", "reference_count", "rejected"),
    [(False, 2, False), (False, 3, True), (True, 1, False), (True, 2, True)],
)
def test_reference_limit_counts_primary_image(
    use_adc: bool, primary: bool, reference_count: int, rejected: bool
) -> None:
    model = _model().model_copy(
        update={
            "parameter_constraints": {
                ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=2)
            }
        }
    )
    client = create_client(
        modality=Modality.IMAGES,
        model=model,
        auth=GoogleADC(project_id="p") if use_adc else _api_key_auth(),
    )
    image = ImageArtifact(data=b"ref", mime_type=ImageMimeType.PNG)
    inputs = ImageInput(prompt="combine", image=image if primary else None)
    references = [image] * reference_count
    if rejected:
        with pytest.raises(ConstraintViolationError, match="at most 2"):
            client._build_request(inputs, reference_images=references)
        return
    request = client._build_request(inputs, reference_images=references)
    parts = (
        request["contents"][0]["parts"] if use_adc else request["input"][0]["content"]
    )
    assert len(parts) == reference_count + int(primary) + 1


@pytest.mark.parametrize("use_adc", [False, True], ids=["api-key", "adc"])
def test_create_client_rejects_unknown_google_images_model(use_adc: bool) -> None:
    model = Model(
        id="unknown-google-image-model",
        provider=Provider.GOOGLE,
        display_name="Unknown Google image model",
        operations={Modality.IMAGES: {Operation.GENERATE}},
    )
    auth = GoogleADC(project_id="p") if use_adc else _api_key_auth()

    with pytest.raises(ValueError, match="Unknown Google images model"):
        create_client(
            modality=Modality.IMAGES,
            provider=Provider.GOOGLE,
            model=model,
            auth=auth,
        )


def test_interactions_init_request_generate_is_text_only() -> None:
    client = GoogleImagesClient(
        model=_model(), provider=Provider.GOOGLE, auth=_api_key_auth()
    )

    request = client._init_request(ImageInput(prompt="a nano banana dish"))

    assert request == {
        "input": [
            {
                "type": "user_input",
                "content": [{"type": "text", "text": "a nano banana dish"}],
            }
        ],
        "response_format": {"type": "image"},
    }


def test_interactions_init_request_edit_prepends_image_part() -> None:
    client = GoogleImagesClient(
        model=_model(), provider=Provider.GOOGLE, auth=_api_key_auth()
    )

    request = client._init_request(
        ImageInput(
            prompt="add a hat",
            image=ImageArtifact(data=b"abc", mime_type=ImageMimeType.PNG),
        )
    )

    content = request["input"][0]["content"]
    assert request["input"][0]["type"] == "user_input"
    assert content[0]["type"] == "image"
    assert content[0]["data"] == "YWJj"
    assert content[1] == {"type": "text", "text": "add a hat"}


def test_interactions_aspect_ratio_and_quality_map_to_response_format() -> None:
    client = GoogleImagesClient(
        model=_model(), provider=Provider.GOOGLE, auth=_api_key_auth()
    )

    request = client._build_request(
        ImageInput(prompt="a nano banana dish"),
        aspect_ratio="16:9",
        quality="2K",
    )

    assert request["response_format"] == {
        "type": "image",
        "aspect_ratio": "16:9",
        "image_size": "2K",
    }


def test_interactions_reference_images_stay_inside_user_input_content() -> None:
    client = GoogleImagesClient(
        model=_model(), provider=Provider.GOOGLE, auth=_api_key_auth()
    )

    request = client._build_request(
        ImageInput(prompt="combine these"),
        reference_images=[ImageArtifact(data=b"ref", mime_type=ImageMimeType.PNG)],
    )

    assert request["input"][0]["type"] == "user_input"
    content = request["input"][0]["content"]
    assert content[0]["type"] == "image"
    assert content[0]["data"] == "cmVm"
    assert content[1] == {"type": "text", "text": "combine these"}


def test_interactions_parse_content_extracts_image_from_model_output_step() -> None:
    client = GoogleInteractionsImagesClient(
        model=_model(), provider=Provider.GOOGLE, auth=_api_key_auth()
    )

    response_data = {
        "id": "v1_abc",
        "status": "completed",
        "steps": [
            {
                "type": "model_output",
                "content": [
                    {"type": "image", "data": "YWJj", "mime_type": "image/png"}
                ],
            }
        ],
    }

    artifact = client._parse_content(response_data)

    assert isinstance(artifact, ImageArtifact)
    assert artifact.data == b"abc"
    assert artifact.mime_type == ImageMimeType.PNG
