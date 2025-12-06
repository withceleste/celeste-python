"""Gradium voice definitions."""

from celeste_speech_generation.voices import Voice

# Flagship Voices - curated high-quality voices from Gradium
GRADIUM_FLAGSHIP_VOICES: list[Voice] = [
    # English (US)
    Voice(
        id="YTpq7expH9539ERJ",
        name="Emma",
        provider="gradium",
        language="en-US",
        gender="female",
        description="A pleasant and smooth female voice ready to assist your customers and also eager to have nice conversations.",
    ),
    Voice(
        id="LFZvm12tW_z0xfGo",
        name="Kent",
        provider="gradium",
        language="en-US",
        gender="male",
        description="A relaxed and authentic American adult voice that connects like a genuine friend.",
    ),
    Voice(
        id="jtEKaLYNn6iif5PR",
        name="Sydney",
        provider="gradium",
        language="en-US",
        gender="female",
        description="A joyful and airy American adult voice that makes corporate training feel helpful and light.",
    ),
    Voice(
        id="KWJiFWu2O9nMPYcR",
        name="John",
        provider="gradium",
        language="en-US",
        gender="male",
        description="A warm low-pitched American adult voice with the resonant quality of a classic radio broadcaster.",
    ),
    # English (GB)
    Voice(
        id="ubuXFxVQwVYnZQhy",
        name="Eva",
        provider="gradium",
        language="en-GB",
        gender="female",
        description="A joyful and dynamic British adult voice ideal for lively conversations.",
    ),
    Voice(
        id="m86j6D7UZpGzHsNu",
        name="Jack",
        provider="gradium",
        language="en-GB",
        gender="male",
        description="A pleasant British voice suited for helpful service, casual conversations, or intense narrations.",
    ),
    # French (FR)
    Voice(
        id="b35yykvVppLXyw_l",
        name="Elise",
        provider="gradium",
        language="fr-FR",
        gender="female",
        description="A warm and smooth French adult voice ideal for friendly conversation and welcoming support.",
    ),
    Voice(
        id="axlOaUiFyOZhy4nv",
        name="Leo",
        provider="gradium",
        language="fr-FR",
        gender="male",
        description="A warm and smooth French adult voice ideal for friendly conversation and welcoming support.",
    ),
    # German (DE)
    Voice(
        id="-uP9MuGtBqAvEyxI",
        name="Mia",
        provider="gradium",
        language="de-DE",
        gender="female",
        description="A joyful and energetic German voice perfect for professional context as well as enthusiastic discussions.",
    ),
    Voice(
        id="0y1VZjPabOBU3rWy",
        name="Maximilian",
        provider="gradium",
        language="de-DE",
        gender="male",
        description="A warm and smooth German adult voice ideal for friendly conversation and professional narration.",
    ),
    # Spanish
    Voice(
        id="B36pbz5_UoWn4BDl",
        name="Valentina",
        provider="gradium",
        language="es-MX",
        gender="female",
        description="A warm and engaging Mexican female voice perfect for natural storytelling and connecting like a genuine friend.",
    ),
    Voice(
        id="xu7iJ_fn2ElcWp2s",
        name="Sergio",
        provider="gradium",
        language="es-ES",
        gender="male",
        description="A warm and smooth Spanish adult voice ideal for friendly conversation and professional narration.",
    ),
    # Portuguese (BR)
    Voice(
        id="pYcGZz9VOo4n2ynh",
        name="Alice",
        provider="gradium",
        language="pt-BR",
        gender="female",
        description="A warm and smooth Brazilian female voice ideal for professional service and pleasant narration or even an enthusiastic conversation!",
    ),
    Voice(
        id="M-FvVo9c-jGR4PgP",
        name="Davi",
        provider="gradium",
        language="pt-BR",
        gender="male",
        description="An engaging and smooth Brazilian adult voice ideal for helpful service and relaxing conversations.",
    ),
]

__all__ = ["GRADIUM_FLAGSHIP_VOICES"]
