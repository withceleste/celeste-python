from celeste.artifacts import ImageArtifact
from celeste.modalities.images.providers.openai.client import OpenAIImagesClient


def test_openai_images_preserve_response_cardinality() -> None:
    client = OpenAIImagesClient.model_construct()

    single = client._parse_content({"data": [{"b64_json": "Zmlyc3Q="}]})
    assert isinstance(single, ImageArtifact)
    assert single.data == b"first"

    multiple = client._parse_content(
        {
            "data": [
                {"b64_json": "Zmlyc3Q="},
                {"url": "https://example.com/second.png"},
            ]
        }
    )
    assert isinstance(multiple, list)
    assert [multiple[0].data, multiple[1].url] == [
        b"first",
        "https://example.com/second.png",
    ]
