"""Unit tests for fal SAM 3 segmentation request/response wiring."""

from typing import Any

from pydantic import SecretStr

from celeste.artifacts import ImageArtifact
from celeste.auth import AuthHeader
from celeste.core import Modality, Operation, Provider
from celeste.modalities.segmentation.io import SegmentationInput
from celeste.modalities.segmentation.providers.fal.client import FalSegmentationClient
from celeste.models import Model
from celeste.types import SegmentationMask


def _client() -> FalSegmentationClient:
    return FalSegmentationClient(
        model=Model(
            id="fal-ai/sam-3/image-rle",
            provider=Provider.FAL,
            display_name="SAM 3 Image RLE",
            operations={Modality.SEGMENTATION: {Operation.SEGMENT}},
        ),
        auth=AuthHeader(
            secret=SecretStr("test"), header="Authorization", prefix="Key "
        ),
    )


def test_init_request_maps_image_url_and_prompt() -> None:
    client = _client()
    image = ImageArtifact(url="https://example.com/truck.jpg")
    request = client._init_request(SegmentationInput(image=image, prompt="wheel"))
    assert request == {
        "image_url": "https://example.com/truck.jpg",
        "prompt": "wheel",
    }


def test_init_request_omits_prompt_when_absent() -> None:
    client = _client()
    image = ImageArtifact(url="https://example.com/truck.jpg")
    request = client._init_request(SegmentationInput(image=image))
    assert request == {"image_url": "https://example.com/truck.jpg"}


def test_parse_content_single_rle_string() -> None:
    client = _client()
    masks = client._parse_content(
        {"rle": "1 2 3 4", "scores": [0.9], "boxes": [[0.1, 0.2, 0.3, 0.4]]}
    )
    assert masks == [
        SegmentationMask(
            rle="1 2 3 4",
            index=0,
            score=0.9,
            box=[0.1, 0.2, 0.3, 0.4],
        )
    ]


def test_parse_content_multiple_rles_with_metadata() -> None:
    client = _client()
    response: dict[str, Any] = {
        "rle": ["a", "b"],
        "metadata": [
            {"index": 0, "score": 0.8, "box": [0.1, 0.1, 0.2, 0.2]},
            {"index": 1, "score": 0.7, "box": [0.3, 0.3, 0.4, 0.4]},
        ],
    }
    masks = client._parse_content(response)
    assert len(masks) == 2
    assert masks[0].rle == "a"
    assert masks[0].score == 0.8
    assert masks[1].rle == "b"
    assert masks[1].index == 1
