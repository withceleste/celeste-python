"""Gradium voice definitions for audio modality."""

from celeste.core import Provider

from ...languages import Language
from ...voices import Voice

# Snapshot 2026-07-14: 66 flagship voices.
# Source: https://docs.gradium.ai/guides/voices/flagship-voices
GRADIUM_VOICES = [
    Voice(
        id=voice_id,
        provider=Provider.GRADIUM,
        name=name,
        description=description,
        languages={Language(language)},
    )
    for voice_id, name, description, language in [
        (
            "NbpkqMVS3CJeq2j8",
            "Zoey",
            "Playful, upbeat and Gen Z energy voice with a standard American accent. Perfect for engaging conversations!",
            "en",
        ),
        (
            "cLONiZ4hQ8VpQ4Sz",
            "Skyler",
            "Breezy, fun and youthful voice with a standard American accent.",
            "en",
        ),
        (
            "7aEKz4P1ogZ0UsRP",
            "Riley",
            "Sporty, bright and approachable voice with standard American accent. Let's go!",
            "en",
        ),
        (
            "vtG8ddh4IN32Otad",
            "Quinn",
            "Snappy, cool and contemporary voice with standard American accent. Great for conversational use cases.",
            "en",
        ),
        (
            "4SZHfMpw-p46Ywgs",
            "Harper",
            "Modern, confident and friendly voice with a standard American accent.",
            "en",
        ),
        (
            "6MFfc37kq0sBjBjy",
            "Sterling",
            "A warm energetic American adult voice with theatrical flair that makes every sentence feel like the start of something big.",
            "en",
        ),
        (
            "_6Aslh2DxfmnRLmP",
            "Russell",
            "A high-energy American adult voice that pushes and encourages with the intensity of someone who genuinely believes in you.",
            "en",
        ),
        (
            "r2sIQdqqoqgRJuXw",
            "Marcus",
            "A high-energy resonant American adult voice that speaks with the unshakeable conviction of someone who's already sold you.",
            "en",
        ),
        (
            "POBHtemksfWQbng0",
            "Garrett",
            "A smooth low-pitched American adult voice with the easy confidence and quiet magnetism of someone who never has to raise his voice.",
            "en",
        ),
        (
            "KUpE0JVhjiIzp1Fk",
            "Damon",
            "A bright American adult voice that lights up with the unfiltered excitement of someone explaining their favorite obsession.",
            "en",
        ),
        (
            "4rdlkbxRv4m3UQTW",
            "Tilly",
            "A bright, welcoming British English adult voice with the warmth of a great receptionist. Perfect for greeting customers and friendly front-line support.",
            "en",
        ),
        (
            "uem82D50GRv2Dwma",
            "Pippa",
            "A confident, upbeat British English adult voice with infectious energy. Perfect for proactive assistants and motivating customer success calls.",
            "en",
        ),
        (
            "6PWnV0Nq4wu7RVBT",
            "Maeve",
            "A sparky, attentive British English adult voice that gets to the point with a smile. Ideal for fast, efficient customer support and helpful voice assistants.",
            "en",
        ),
        (
            "gDT1nz7Ie36ZhL-C",
            "Imogen",
            "A bubbly, friendly British English adult voice that puts callers instantly at ease. Great for onboarding assistants and warm concierge interactions.",
            "en",
        ),
        (
            "dME3IWyZBvmh1n1q",
            "Toby",
            "A sparky, attentive British English adult voice that gets to the point with a smile. Ideal for fast, efficient customer support and helpful voice assistants.",
            "en",
        ),
        (
            "CF0NgaMwHMMrHZn0",
            "Reuben",
            "A confident, upbeat British English adult voice with infectious energy. Perfect for proactive assistants and motivating customer success calls.",
            "en",
        ),
        (
            "s_k3kLBbgeK9-xUg",
            "Freddie",
            "An easy-going, friendly British English adult voice that puts callers instantly at ease. Great for onboarding assistants and warm concierge interactions.",
            "en",
        ),
        (
            "kfzLbcdE_yXgLeUI",
            "Archie",
            "A bright, welcoming British English adult voice with the warmth of a great receptionist. Perfect for greeting customers and friendly front-line support.",
            "en",
        ),
        (
            "jBULVCDhf05tOJN5",
            "Romane",
            "A confident, upbeat French adult voice with infectious energy. Perfect for proactive assistants and motivating customer success calls.",
            "fr",
        ),
        (
            "J8c9KBRYAGGYwjns",
            "Margaux",
            "A bright, welcoming French adult voice with the warmth of a great receptionist. Perfect for greeting customers and friendly front-line support.",
            "fr",
        ),
        (
            "3hQIj8JOo7bU31Jw",
            "Garance",
            "A vibrant, engaging French adult voice that makes every explanation feel personal. Built for product guides and walk-through assistants.",
            "fr",
        ),
        (
            "P4GqVY98hjQSvkiu",
            "Capucine",
            "A bubbly, friendly French adult voice that puts callers instantly at ease. Great for onboarding assistants and warm concierge interactions.",
            "fr",
        ),
        (
            "6oIkS98REoVZ1dEw",
            "Apolline",
            "A sparky, attentive French adult voice that gets to the point with a smile. Ideal for fast, efficient customer support and helpful voice assistants.",
            "fr",
        ),
        (
            "biuhvu17TxVKOcyy",
            "Marius",
            "An energetic, well-poised French adult voice with the confident assurance of a natural closer. Ideal for sales pitches and high-conviction content.",
            "fr",
        ),
        (
            "YKeBw3OV1RgpdhLh",
            "Jules",
            "A lively, expressive French adult voice that lights up around topics it loves. Great for animated recommendations and high-energy dialogue.",
            "fr",
        ),
        (
            "iEu63s1rhn_kegTr",
            "Gaspard",
            "A warm, grounded French adult voice with the easy confidence of a trusted friend. Ideal for friendly assistants and peer-to-peer dialogue.",
            "fr",
        ),
        (
            "25AzBFyp6svYnJsj",
            "Damien",
            "An intense, engaging French adult voice that pushes with real conviction. Built for coaching and motivational content.",
            "fr",
        ),
        (
            "Tek4tJXiX6_yvXq7",
            "Augustin",
            "A curious, animated French adult voice that lights up when sharing an unexpected fact. Perfect for geeky explainers and trivia-driven dialogue.",
            "fr",
        ),
        (
            "mmLFHtCjt_6jw0vT",
            "Roxane",
            "A calm, attentive Québécois French adult voice that gets to the point with a smile. Ideal for efficient customer support and helpful voice assistants.",
            "fr",
        ),
        (
            "sX0PcxM_Ie2ctBGH",
            "Frédérique",
            "A confident, upbeat Québécois French adult voice with infectious energy. Perfect for proactive assistants and motivating customer success calls.",
            "fr",
        ),
        (
            "sBLwTd5womVX8JOw",
            "Maude",
            "A bubbly, reassuring Québécois French (FR-CA) adult voice that puts callers instantly at ease. Great for onboarding assistants and step-by-step guidance.",
            "fr",
        ),
        (
            "SqFfhmAgR2XdN83R",
            "Svenja",
            "A confident, upbeat German adult voice with infectious energy. Perfect for proactive assistants and motivating customer success calls.",
            "de",
        ),
        (
            "6XwZeudK_gn719g5",
            "Ronja",
            "A vibrant, engaging German adult voice that makes every explanation feel personal. Built for product guides and walk-through assistants.",
            "de",
        ),
        (
            "nMNZ0sOWZVbKyjaI",
            "Mila",
            "A bright, welcoming German adult voice with the warmth of a great receptionist. Perfect for greeting customers and friendly front-line support.",
            "de",
        ),
        (
            "yHyu3PRfSmmiL2a4",
            "Marlene",
            "A bubbly, friendly German adult voice that puts callers instantly at ease. Great for onboarding assistants and warm concierge interactions.",
            "de",
        ),
        (
            "p6Uutkyi3j2iNAUu",
            "Annika",
            "A sparky, attentive German adult voice that gets to the point with a smile. Ideal for fast, efficient customer support and helpful voice assistants.",
            "de",
        ),
        (
            "Kf5m22mROozoMWj3",
            "Mats",
            "A sparky, attentive German adult voice that gets to the point with a smile. Ideal for fast, efficient customer support and helpful voice assistants.",
            "de",
        ),
        (
            "20zdyYrQPzKlCwkk",
            "Leon",
            "A bright, welcoming German adult voice with the warmth of a great receptionist. Perfect for greeting customers and friendly front-line support.",
            "de",
        ),
        (
            "yyS1KYWs6mXoEw7D",
            "Henrik",
            "An easy-going, friendly German adult voice that puts callers instantly at ease. Great for onboarding assistants and warm concierge interactions.",
            "de",
        ),
        (
            "lbpBQTVCOcOHJ5zS",
            "Erik",
            "A confident, upbeat German adult voice with infectious energy. Perfect for proactive assistants and motivating customer success calls.",
            "de",
        ),
        (
            "3ZKKapPOvuWFcw9f",
            "Anton",
            "A vibrant, engaging German adult voice that makes every explanation feel personal. Built for product guides and walk-through assistants.",
            "de",
        ),
        (
            "TXbEUrHXNFlYBBKb",
            "Sophie",
            "A warm, easy-going Austrian German adult voice with effortless local charm. Perfect for friendly assistants and welcoming customer support.",
            "de",
        ),
        (
            "Xtp0vUDvtAfi1xkH",
            "Stefan",
            "A composed, welcoming Austrian German adult voice with the calm reliability of a trusted advisor. Ideal for professional support and onboarding interactions.",
            "de",
        ),
        (
            "BPHlOW9jPs79KtW4",
            "Maxi",
            "A playful, expressive Austrian German adult voice that brings warmth and humor to every interaction. Great for engaging assistants and conversational AI.",
            "de",
        ),
        (
            "m3lIeODdTQ3bOh4z",
            "Vega",
            "A sparky, attentive Peninsular Spanish adult voice that gets to the point with a smile. Ideal for fast, efficient customer support and helpful voice assistants.",
            "es",
        ),
        (
            "hP6WA-7ybEGApJ68",
            "Paula",
            "A bubbly, friendly Peninsular Spanish adult voice that puts callers instantly at ease. Great for onboarding assistants and warm concierge interactions.",
            "es",
        ),
        (
            "A3UKMLXQUzknYpQa",
            "Lucia",
            "A bright, welcoming Peninsular Spanish adult voice with the warmth of a great receptionist. Perfect for greeting customers and friendly front-line support.",
            "es",
        ),
        (
            "9UogMEa01dHR9Xbc",
            "Aitana",
            "A confident, upbeat Peninsular Spanish adult voice with infectious energy. Perfect for proactive assistants and motivating customer success calls.",
            "es",
        ),
        (
            "sVLgzKMqaptUdaY8",
            "Mateo",
            "A sparky, attentive Peninsular Spanish adult voice that gets to the point with a smile. Ideal for fast, efficient customer support and helpful voice assistants.",
            "es",
        ),
        (
            "jvPx8j8zLGQ3utZz",
            "Marcos",
            "A confident, upbeat Peninsular Spanish adult voice with infectious energy. Perfect for proactive assistants and motivating customer success calls.",
            "es",
        ),
        (
            "t-_TS1e-0GzDAX02",
            "Iker",
            "An easy-going, friendly Peninsular Spanish adult voice that puts callers instantly at ease. Great for onboarding assistants and warm concierge interactions.",
            "es",
        ),
        (
            "ZeL1KGaZ4BZ2w0Np",
            "Alvaro",
            "A bright, welcoming Peninsular Spanish adult voice with the warmth of a great receptionist. Perfect for greeting customers and friendly front-line support.",
            "es",
        ),
        (
            "4NLtOv1m0azv9rGL",
            "Camila",
            "A warm, welcoming Mexican Spanish adult voice with the easy hospitality of a great host. Perfect for greeting customers and friendly front-line support.",
            "es",
        ),
        (
            "VDwnGxAo68C8U8vC",
            "Ximena",
            "A playful, expressive Mexican Spanish adult voice that turns everyday moments into stories. Great for engaging assistants and personable conversational AI.",
            "es",
        ),
        (
            "s58clrg2fe0MO7Y-",
            "Regina",
            "A confident, upbeat Mexican Spanish adult voice with the natural assurance of a closer. Ideal for proactive assistants and sales-led customer interactions.",
            "es",
        ),
        (
            "yHToO6ssaQHz5kIP",
            "Santiago",
            "A warm, welcoming Mexican Spanish adult voice with calm professional reassurance. Perfect for greeting customers and friendly front-line support.",
            "es",
        ),
        (
            "n7vovxcDTVG4gClo",
            "Diego",
            "A lively, expressive Mexican Spanish adult voice with natural storytelling flair. Great for animated assistants and engaging conversational AI.",
            "es",
        ),
        (
            "tWll9uiMafMXfOGw",
            "Emiliano",
            "An assured, upbeat Mexican Spanish adult voice with a touch of humor. Built for confident product guides and proactive customer success.",
            "es",
        ),
        (
            "YnWEONxJy7ptGhfb",
            "Yara",
            "A vibrant, engaging Brazilian Portuguese adult voice that makes every explanation feel personal. Built for product guides and walk-through assistants.",
            "pt",
        ),
        (
            "fd7e1fLVAAJzzs8P",
            "Manuela",
            "A confident, upbeat Brazilian Portuguese adult voice with infectious energy. Perfect for proactive assistants and motivating customer success calls.",
            "pt",
        ),
        (
            "DUFZMTh4n-53Ly9O",
            "Larissa",
            "A bubbly, friendly Brazilian Portuguese adult voice that puts callers instantly at ease. Great for onboarding assistants and warm concierge interactions.",
            "pt",
        ),
        (
            "ycGyxoEy9wLaX11R",
            "Helena",
            "A sparky, attentive Brazilian Portuguese adult voice that gets to the point with a smile. Ideal for fast, efficient customer support and helpful voice assistants.",
            "pt",
        ),
        (
            "uCqxlQCKi8sPHwG2",
            "Bianca",
            "A bright, welcoming Brazilian Portuguese adult voice with the warmth of a great receptionist. Perfect for greeting customers and friendly front-line support.",
            "pt",
        ),
        (
            "AByHrwi1S-yLzW-s",
            "Mateus",
            "A bright, welcoming Brazilian Portuguese adult voice with the warmth of a great receptionist. Perfect for greeting customers and friendly front-line support.",
            "pt",
        ),
        (
            "NuUr_x5V90hSHzCJ",
            "Davi",
            "A confident, upbeat Brazilian Portuguese adult voice with infectious energy. Perfect for proactive assistants and motivating customer success calls.",
            "pt",
        ),
        (
            "Qit9Oc9fEO9yXsVw",
            "Caio",
            "A sparky, attentive Brazilian Portuguese adult voice that gets to the point with a smile. Ideal for fast, efficient customer support and helpful voice assistants.",
            "pt",
        ),
    ]
]

__all__ = ["GRADIUM_VOICES"]
