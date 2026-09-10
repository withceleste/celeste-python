from celeste.artifacts import ImageArtifact
from celeste.mime_types import ImageMimeType
from celeste.modalities.images.providers.xai.client import XAIImagesClient


def test_parse_content_preserves_order_cardinality_and_item_metadata() -> None:
    content = XAIImagesClient.model_construct()._parse_content(
        {
            "data": [
                {
                    "url": "https://example.com/first.png",
                    "mime_type": "image/png",
                    "revised_prompt": "first revised",
                    "file_output": {"file_id": "file-1"},
                },
                {
                    "b64_json": "c2Vjb25k",
                    "mime_type": "image/webp",
                    "respect_moderation": True,
                },
            ]
        }
    )

    assert isinstance(content, list)
    assert content == [
        ImageArtifact(
            url="https://example.com/first.png",
            mime_type=ImageMimeType.PNG,
            metadata={
                "revised_prompt": "first revised",
                "file_output": {"file_id": "file-1"},
            },
        ),
        ImageArtifact(
            data=b"second",
            mime_type=ImageMimeType.WEBP,
            metadata={"respect_moderation": True},
        ),
    ]


def test_parse_content_keeps_single_output_singular() -> None:
    content = XAIImagesClient.model_construct()._parse_content(
        {"data": [{"url": "https://example.com/only.png"}]}
    )

    assert isinstance(content, ImageArtifact)
