"""Unit tests for BFL images provider model-family dispatch and edit image field."""

import pytest
from pydantic import SecretStr

from celeste import Model, create_client, get_model
from celeste.artifacts import ImageArtifact
from celeste.auth import AuthHeader
from celeste.core import Modality, Operation, Provider
from celeste.modalities.images.client import ImagesClient
from celeste.modalities.images.io import ImageInput
from celeste.modalities.images.providers.bfl.client import BFLImagesClient
from celeste.modalities.images.providers.bfl.flux1 import BFLFlux1ImagesClient
from celeste.modalities.images.providers.bfl.flux2 import BFLFlux2ImagesClient
from celeste.modalities.images.providers.bfl.flux3 import BFLFlux3ImagesClient
from celeste.modalities.images.providers.bfl.kontext import BFLKontextImagesClient

IMAGE = ImageArtifact(url="https://example.com/image.png")


def _auth() -> AuthHeader:
    return AuthHeader(secret=SecretStr("test"), header="x-key", prefix="")


@pytest.mark.parametrize(
    ("model_id", "backend", "edit_image"),
    [
        ("flux-3-image", BFLFlux3ImagesClient, {"images": [IMAGE.url]}),
        ("flux-2-pro", BFLFlux2ImagesClient, {"input_image": IMAGE.url}),
        ("flux-kontext-pro", BFLKontextImagesClient, {"input_image": IMAGE.url}),
        ("flux-dev", BFLFlux1ImagesClient, {}),
    ],
)
def test_model_family_selects_backend_and_edit_image_field(
    model_id: str, backend: type[ImagesClient], edit_image: dict[str, object]
) -> None:
    model = get_model(model_id, provider=Provider.BFL)
    assert model is not None
    client = BFLImagesClient(model=model, provider=Provider.BFL, auth=_auth())

    assert isinstance(client._strategy, backend)
    assert client._generate_endpoint == client._strategy._generate_endpoint
    assert client._edit_endpoint == client._strategy._edit_endpoint
    assert client._init_request(ImageInput(prompt="p", image=IMAGE)) == {
        "prompt": "p",
        **edit_image,
    }


def test_create_client_rejects_unknown_bfl_images_model() -> None:
    model = Model(
        id="unknown-bfl-image-model",
        provider=Provider.BFL,
        display_name="Unknown BFL image model",
        operations={Modality.IMAGES: {Operation.GENERATE}},
    )

    with pytest.raises(ValueError, match="Unknown BFL images model"):
        create_client(
            modality=Modality.IMAGES,
            provider=Provider.BFL,
            model=model,
            auth=_auth(),
        )
