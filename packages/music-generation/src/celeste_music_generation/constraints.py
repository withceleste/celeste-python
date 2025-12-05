"""Constraints for music generation parameters."""

from celeste.constraints import Choice, Range

# Duration constraints (in seconds)
DURATION_RANGE = Range(min=5, max=600)  # 5 seconds to 10 minutes

# Tempo constraints (BPM)
TEMPO_RANGE = Range(min=40, max=240)

# Quality choices (common across providers)
QUALITY_CHOICES = Choice(options=["low", "standard", "high", "premium"])

# Vocal gender choices
VOCAL_GENDER_CHOICES = Choice(options=["male", "female", "neutral", "mixed"])

# Common genre choices
GENRE_CHOICES = Choice(
    options=[
        "pop",
        "rock",
        "jazz",
        "classical",
        "electronic",
        "hip-hop",
        "country",
        "r&b",
        "metal",
        "folk",
        "blues",
        "reggae",
        "latin",
        "ambient",
        "instrumental",
    ]
)

# Mood choices
MOOD_CHOICES = Choice(
    options=[
        "happy",
        "sad",
        "energetic",
        "calm",
        "melancholic",
        "romantic",
        "aggressive",
        "mysterious",
        "uplifting",
        "dark",
    ]
)

# Musical keys
KEY_CHOICES = Choice(
    options=[
        "C major",
        "C minor",
        "D major",
        "D minor",
        "E major",
        "E minor",
        "F major",
        "F minor",
        "G major",
        "G minor",
        "A major",
        "A minor",
        "B major",
        "B minor",
    ]
)


__all__ = [
    "DURATION_RANGE",
    "GENRE_CHOICES",
    "KEY_CHOICES",
    "MOOD_CHOICES",
    "QUALITY_CHOICES",
    "TEMPO_RANGE",
    "VOCAL_GENDER_CHOICES",
]
