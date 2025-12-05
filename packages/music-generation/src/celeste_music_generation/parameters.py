"""Parameters for music generation."""

from enum import StrEnum

from celeste.parameters import Parameters


class MusicGenerationParameter(StrEnum):
    """Music generation parameter names."""

    # Core parameters
    DURATION = "duration"
    STREAM = "stream"
    QUALITY = "quality"
    STYLE = "style"
    GENRE = "genre"
    TEMPO = "tempo"
    KEY = "key"
    MOOD = "mood"

    # Reference audio parameters
    REFERENCE_AUDIO = "reference_audio"
    REFERENCE_MELODY = "reference_melody"
    REFERENCE_VOCAL = "reference_vocal"
    REFERENCE_ID = "reference_id"  # Mureka-specific reference ID
    VOCAL_ID = "vocal_id"  # Mureka-specific vocal ID
    MELODY_ID = "melody_id"  # Mureka-specific melody ID

    # Generation parameters
    N = "n"  # Number of outputs to generate

    # Lyrics parameters
    LYRICS = "lyrics"
    VOCAL_GENDER = "vocal_gender"
    VOCAL_STYLE = "vocal_style"

    # Advanced parameters
    INSTRUMENTAL_ONLY = "instrumental_only"
    EXTEND_FROM = "extend_from"
    SONG_ID = "song_id"  # For extend_song
    UPLOAD_AUDIO_ID = "upload_audio_id"  # For extend_song
    EXTEND_AT = "extend_at"  # For extend_song (milliseconds)
    INSTRUMENTAL_ID = "instrumental_id"  # Mureka-specific for instrumental reference


class MusicGenerationParameters(Parameters, total=False):
    """TypedDict for music generation parameters.

    All fields are optional to support provider flexibility.
    """

    # Core parameters
    duration: int  # Duration in seconds
    stream: bool  # Enable streaming
    quality: str  # Quality level (e.g., "standard", "high")
    style: str  # Music style description
    genre: str  # Genre (e.g., "rock", "jazz", "electronic")
    tempo: int  # BPM (beats per minute)
    key: str  # Musical key (e.g., "C major", "A minor")
    mood: str  # Mood/emotion (e.g., "happy", "melancholic")

    # Reference audio parameters
    reference_audio: str  # Reference audio file ID or URL
    reference_melody: str  # Melody reference file ID
    reference_vocal: str  # Vocal reference file ID
    reference_id: str  # Mureka-specific reference ID
    vocal_id: str  # Mureka-specific vocal ID
    melody_id: str  # Mureka-specific melody ID

    # Generation parameters
    n: int  # Number of outputs to generate

    # Lyrics parameters
    lyrics: str  # Song lyrics text
    vocal_gender: str  # Vocal gender (e.g., "male", "female", "neutral")
    vocal_style: str  # Vocal style (e.g., "pop", "opera")

    # Advanced parameters
    instrumental_only: bool  # Generate instrumental only (no vocals)
    extend_from: str  # Task ID or file to extend from
    song_id: str  # Song ID for extending (from song/generate)
    upload_audio_id: str  # Upload ID for extending (from files/upload)
    extend_at: int  # Extending start time in milliseconds [8000, 420000]
    instrumental_id: str  # Instrumental reference ID


__all__ = [
    "MusicGenerationParameter",
    "MusicGenerationParameters",
]
