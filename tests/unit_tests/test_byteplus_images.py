import pytest

from celeste import Modality, create_client
from celeste.auth import NoAuth
from celeste.exceptions import ConstraintViolationError
from celeste.modalities.images.io import ImageInput


def test_pro_exact_dimensions_need_no_sixteen_pixel_alignment() -> None:
    client = create_client(
        modality=Modality.IMAGES,
        model="dola-seedream-5-0-pro-260628",
        auth=NoAuth(),
    )
    inputs = ImageInput(prompt="A red circle")
    request = client._build_request(inputs, aspect_ratio="1500x1000")
    assert request["size"] == "1500x1000"
    for size in ("512x512", "4096x4096", "4096x240"):
        with pytest.raises(ConstraintViolationError):
            client._build_request(inputs, aspect_ratio=size)
