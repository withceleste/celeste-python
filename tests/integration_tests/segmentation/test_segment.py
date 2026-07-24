"""Integration tests for fal SAM 3 segmentation."""

import os

import pytest

from celeste import Modality, Provider, create_client
from celeste.artifacts import ImageArtifact
from celeste.modalities.segmentation import SegmentationOutput
from celeste.types import SegmentationMask

TRUCK = (
    "https://raw.githubusercontent.com/facebookresearch/segment-anything-2/"
    "main/notebooks/images/truck.jpg"
)


@pytest.mark.skipif(not os.getenv("FAL_KEY"), reason="FAL_KEY not set")
@pytest.mark.parametrize(
    "model",
    ["fal-ai/sam-3/image-rle", "fal-ai/sam-3-1/image-rle"],
)
async def test_segment_image_rle(model: str) -> None:
    client = create_client(
        modality=Modality.SEGMENTATION,
        provider=Provider.FAL,
        model=model,
    )
    response = await client.segment(
        image=ImageArtifact(url=TRUCK),
        prompt="wheel",
        include_scores=True,
        include_boxes=True,
        return_multiple_masks=True,
        max_masks=3,
    )

    assert isinstance(response, SegmentationOutput)
    assert isinstance(response.content, list)
    assert response.content
    assert all(isinstance(mask, SegmentationMask) for mask in response.content)
    assert all(mask.rle for mask in response.content)
