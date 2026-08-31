import pytest

from celeste.artifacts import ImageArtifact
from celeste.modalities.images.client import ImagesStreamNamespace, ImagesSyncNamespace
from celeste.models import Model


class _Client:
    model = Model(id="image-model", display_name="Image model", streaming=True)
    _generate_endpoint = "/generate"
    _edit_endpoint = "/edit"
    _upscale_endpoint = "/upscale"

    def __init__(self) -> None:
        self.endpoints: list[str | None] = []

    async def _predict(
        self, inputs: object, *, endpoint: str | None = None, **_: object
    ) -> str:
        self.endpoints.append(endpoint)
        return "output"

    def _stream(
        self, inputs: object, *, endpoint: str | None = None, **_: object
    ) -> str:
        self.endpoints.append(endpoint)
        return "stream"

    def _stream_class(self) -> type:
        return object


def test_image_namespaces_route_each_operation_to_its_endpoint() -> None:
    client = _Client()
    image = ImageArtifact(url="https://example.com/image.png")

    sync = ImagesSyncNamespace(client)  # type: ignore[arg-type]
    sync.generate("new")
    sync.edit(image, "change")
    sync.upscale(image)

    stream = ImagesStreamNamespace(client)  # type: ignore[arg-type]
    stream.generate("new")
    stream.edit(image, "change")

    assert client.endpoints == ["/generate", "/edit", "/upscale", "/generate", "/edit"]


def test_image_namespaces_reject_unsupported_edit() -> None:
    client = _Client()
    client._edit_endpoint = None
    image = ImageArtifact(url="https://example.com/image.png")

    with pytest.raises(NotImplementedError, match="does not support image editing"):
        ImagesSyncNamespace(client).edit(image, "change")  # type: ignore[arg-type]
    with pytest.raises(NotImplementedError, match="does not support image editing"):
        ImagesStreamNamespace(client).edit(image, "change")  # type: ignore[arg-type]
