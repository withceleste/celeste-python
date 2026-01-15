"""Gradium voice definitions for audio modality."""

from celeste.core import Provider

from ...voices import Voice

# Gradium flagship voices
# Full list at https://gradium.ai/api_dpocs.html
GRADIUM_VOICES = [
    # English (US)
    Voice(
        id="YTpq7expH9539ERJ",
        provider=Provider.GRADIUM,
        name="Emma",
        languages={"en"},
    ),
    Voice(
        id="LFZvm12tW_z0xfGo",
        provider=Provider.GRADIUM,
        name="Kent",
        languages={"en"},
    ),
    Voice(
        id="jtEKaLYNn6iif5PR",
        provider=Provider.GRADIUM,
        name="Sydney",
        languages={"en"},
    ),
    Voice(
        id="KWJiFWu2O9nMPYcR",
        provider=Provider.GRADIUM,
        name="John",
        languages={"en"},
    ),
    # English (GB)
    Voice(
        id="ubuXFxVQwVYnZQhy",
        provider=Provider.GRADIUM,
        name="Eva",
        languages={"en"},
    ),
    Voice(
        id="m86j6D7UZpGzHsNu",
        provider=Provider.GRADIUM,
        name="Jack",
        languages={"en"},
    ),
    # French
    Voice(
        id="b35yykvVppLXyw_l",
        provider=Provider.GRADIUM,
        name="Elise",
        languages={"fr"},
    ),
    Voice(
        id="axlOaUiFyOZhy4nv",
        provider=Provider.GRADIUM,
        name="Leo",
        languages={"fr"},
    ),
    # German
    Voice(
        id="-uP9MuGtBqAvEyxI",
        provider=Provider.GRADIUM,
        name="Mia",
        languages={"de"},
    ),
    Voice(
        id="0y1VZjPabOBU3rWy",
        provider=Provider.GRADIUM,
        name="Maximilian",
        languages={"de"},
    ),
    # Spanish
    Voice(
        id="B36pbz5_UoWn4BDl",
        provider=Provider.GRADIUM,
        name="Valentina",
        languages={"es"},
    ),
    Voice(
        id="xu7iJ_fn2ElcWp2s",
        provider=Provider.GRADIUM,
        name="Sergio",
        languages={"es"},
    ),
    # Portuguese (Brazilian)
    Voice(
        id="pYcGZz9VOo4n2ynh",
        provider=Provider.GRADIUM,
        name="Alice",
        languages={"pt"},
    ),
    Voice(
        id="M-FvVo9c-jGR4PgP",
        provider=Provider.GRADIUM,
        name="Davi",
        languages={"pt"},
    ),
]

__all__ = ["GRADIUM_VOICES"]
