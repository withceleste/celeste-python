"""Regression coverage for Gemini grounding source domains."""

from celeste.modalities.text.providers.google.grounding import map_grounding


def test_maps_google_grounding_source_domains() -> None:
    grounding = map_grounding(
        {
            "groundingChunks": [
                {
                    "web": {
                        "uri": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/example",
                        "title": "aljazeera.com",
                    }
                },
                {
                    "web": {
                        "uri": "https://example.com/article",
                        "title": "Article title",
                        "domain": "example.com",
                    }
                },
            ]
        },
        "",
    )

    assert [source.domain for source in grounding.sources] == [
        "aljazeera.com",
        "example.com",
    ]
