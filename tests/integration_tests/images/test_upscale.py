import pytest

from celeste import Modality, Operation, Provider, create_client
from celeste.artifacts import ImageArtifact
from celeste.modalities.images import ImageOutput, ImageUsage


@pytest.mark.parametrize(
    ("model",),
    [
        ("Standard V2",),
    ],
)
async def test_upscale(model: str, square_image: ImageArtifact) -> None:
    client = create_client(
        modality=Modality.IMAGES,
        operation=Operation.UPSCALE,
        provider=Provider.TOPAZLABS,
        model=model,
    )

    response = await client.upscale(image=square_image, output_format="jpeg")

    assert isinstance(response, ImageOutput)
    assert isinstance(response.content, ImageArtifact)
    assert response.content.has_content
    assert isinstance(response.usage, ImageUsage)
