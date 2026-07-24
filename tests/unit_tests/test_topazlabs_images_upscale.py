"""Unit tests for Topaz Labs image upscale request building."""

import pytest
from pydantic import SecretStr

from celeste.artifacts import ImageArtifact
from celeste.auth import AuthHeader
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import ImageMimeType
from celeste.modalities.images.io import ImageInput
from celeste.modalities.images.providers.topazlabs.client import TopazLabsImagesClient
from celeste.modalities.images.providers.topazlabs.models import MODELS
from celeste.models import Model
from celeste.providers.topazlabs.image import config
from celeste.providers.topazlabs.image.client import form_field_value


def _client(model_id: str = "Standard V2") -> TopazLabsImagesClient:
    return TopazLabsImagesClient(
        model=Model(
            id=model_id,
            provider=Provider.TOPAZLABS,
            display_name=model_id,
            operations={Modality.IMAGES: {Operation.UPSCALE}},
        ),
        auth=AuthHeader(secret=SecretStr("test")),
        provider=Provider.TOPAZLABS,
    )


def test_init_request_puts_image_artifact() -> None:
    image = ImageArtifact(data=b"fake-image", mime_type=ImageMimeType.PNG)
    request = _client()._init_request(ImageInput(image=image))
    assert request == {"image": image}


def test_build_request_adds_model() -> None:
    image = ImageArtifact(data=b"fake-image", mime_type=ImageMimeType.JPEG)
    client = _client()
    request = client._build_request(
        ImageInput(image=image), output_format="jpeg", strength=0.5
    )
    assert request["image"] is image
    assert request["model"] == "Standard V2"
    assert request["output_format"] == "jpeg"
    assert request["strength"] == 0.5


def test_build_request_maps_text_refine_denoise_strength() -> None:
    image = ImageArtifact(data=b"fake-image", mime_type=ImageMimeType.PNG)
    client = _client("Text Refine")
    request = client._build_request(
        ImageInput(image=image), denoise_strength=0.5, decompression_strength=0.4
    )
    assert request["model"] == "Text Refine"
    assert request["denoise_strength"] == 0.5
    assert request["decompression_strength"] == 0.4


def test_parse_content_prefers_download_url() -> None:
    artifact = _client()._parse_content(
        {"download_url": "https://example.com/out.jpg", "url": "https://other"}
    )
    assert isinstance(artifact, ImageArtifact)
    assert artifact.url == "https://example.com/out.jpg"


def test_parse_content_falls_back_to_url() -> None:
    artifact = _client()._parse_content({"url": "https://example.com/out.jpg"})
    assert artifact.url == "https://example.com/out.jpg"


@pytest.mark.parametrize(
    ("model_id", "endpoint"),
    [
        ("Standard V2", config.TopazLabsImageEndpoint.ENHANCE_ASYNC),
        ("High Fidelity V2", config.TopazLabsImageEndpoint.ENHANCE_ASYNC),
        ("Upscale High Fidelity V3", config.TopazLabsImageEndpoint.ENHANCE_ASYNC),
        ("Low Resolution V2", config.TopazLabsImageEndpoint.ENHANCE_ASYNC),
        ("CGI", config.TopazLabsImageEndpoint.ENHANCE_ASYNC),
        ("Text Refine", config.TopazLabsImageEndpoint.ENHANCE_ASYNC),
        ("Detail", config.TopazLabsImageEndpoint.ENHANCE_GEN_ASYNC),
        ("Transparency Upscale", config.TopazLabsImageEndpoint.TOOL_ASYNC),
    ],
)
def test_submit_endpoint_for_model(model_id: str, endpoint: str) -> None:
    assert config.submit_endpoint_for_model(model_id) == endpoint


def test_submit_endpoint_unknown_model_fails() -> None:
    with pytest.raises(KeyError, match="No Topaz Image submit endpoint"):
        config.submit_endpoint_for_model("Unknown Model")


def test_catalog_models_have_submit_endpoints() -> None:
    catalog_ids = {model.id for model in MODELS}
    assert catalog_ids == set(config.SUBMIT_ENDPOINT_BY_MODEL)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (True, "true"),
        (False, "false"),
        (0.5, "0.5"),
        (1, "1"),
        ("jpeg", "jpeg"),
    ],
)
def test_form_field_value_encodes_bools_lowercase(value: object, expected: str) -> None:
    assert form_field_value(value) == expected
