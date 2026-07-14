"""ElevenLabs voice definitions for audio modality."""

from celeste.core import Provider

from ...voices import Voice

# Snapshot 2026-07-14: 21 default voices from GET /v2/voices?voice_type=default.
# Source: https://elevenlabs.io/docs/api-reference/voices/search
ELEVENLABS_VOICES = [
    Voice(
        id=voice_id,
        provider=Provider.ELEVENLABS,
        name=name,
        description=description,
    )
    for voice_id, name, description in [
        (
            "pNInz6obpgDQGcFmaJgB",
            "Adam - Dominant, Firm",
            "A bright tenor pitch that immediately cuts through. The delivery is brash and openly confident, speaking with unwavering certainty and a slightly aggressive self-assurance.",
        ),
        (
            "Xb7hH8MSUJpSbSDYk0k2",
            "Alice - Clear, Engaging Educator",
            "Clear and engaging, friendly woman with a British accent suitable for e-learning.",
        ),
        (
            "hpp4J3VqNfWAUOO0d1Us",
            "Bella - Professional, Bright, Warm",
            "This voice is warm, bright, and professional, characterized by a Standard American accent and a polished, narrative quality. It features a medium-high pitch with crisp diction and a deliberate, rhythmic pace that makes it highly intelligible and engaging for long-form listening.",
        ),
        (
            "pqHfZKP75CvOlQylNhV4",
            "Bill - Wise, Mature, Balanced",
            "Friendly and comforting voice ready to narrate your stories.",
        ),
        (
            "nPczCjzI2devNBz1zQrb",
            "Brian - Deep, Resonant and Comforting",
            "Middle-aged man with a resonant and comforting tone. Great for narrations and advertisements.",
        ),
        (
            "N2lVS1w4EtoT3dr4eOWO",
            "Callum - Husky Trickster",
            "Deceptively gravelly, yet unsettling edge.",
        ),
        (
            "IKne3meq5aSn9XLyUdCD",
            "Charlie - Deep, Confident, Energetic",
            "A young Australian male with a confident and energetic voice.",
        ),
        (
            "iP95p4xoKVk53GoZ742B",
            "Chris - Charming, Down-to-Earth",
            "Natural and real, this down-to-earth voice is great across many use-cases.",
        ),
        (
            "onwK4e9ZLuTAKqWW03F9",
            "Daniel - Steady Broadcaster",
            "A strong voice perfect for delivering a professional broadcast or news story.",
        ),
        (
            "cjVigY5qzO86Huf0OWal",
            "Eric - Smooth, Trustworthy",
            "A smooth tenor pitch from a man in his 40s - perfect for agentic use cases.",
        ),
        (
            "JBFqnCBsd6RMkjVDRZzb",
            "George - Warm, Captivating Storyteller",
            "Warm resonance that instantly captivates listeners.",
        ),
        (
            "SOYHLrjzK2X1ezoPC6cr",
            "Harry - Fierce Warrior",
            "An animated warrior ready to charge forward.",
        ),
        (
            "cgSgspJ2msm6clMCkdW9",
            "Jessica - Playful, Bright, Warm",
            "Young and popular, this playful American female voice is perfect for trendy content.",
        ),
        (
            "FGY2WhTYpPnrIDTdsKH5",
            "Laura - Enthusiast, Quirky Attitude",
            "This young adult female voice delivers sunny enthusiasm with a quirky attitude.",
        ),
        (
            "TX3LPaxmHKxFdv7VOQHJ",
            "Liam - Energetic, Social Media Creator",
            "A young adult with energy and warmth - suitable for reels and shorts.",
        ),
        (
            "pFZP5JQG7iQjIQuC4Bku",
            "Lily - Velvety Actress",
            "Velvety British female voice delivers news and narrations with warmth and clarity.",
        ),
        (
            "XrExE9yKIg1WjnnlVkGX",
            "Matilda - Knowledgable, Professional",
            "A professional woman with a pleasing alto pitch. Suitable for many use cases.",
        ),
        (
            "SAz9YHcvj6GT2YYXdXww",
            "River - Relaxed, Neutral, Informative",
            "A relaxed, neutral voice ready for narrations or conversational projects.",
        ),
        (
            "CwhRBWXzGAHq8TQ4Fs17",
            "Roger - Laid-Back, Casual, Resonant",
            "Easy going and perfect for casual conversations.",
        ),
        (
            "EXAVITQu4vr4xnSDxMaL",
            "Sarah - Mature, Reassuring, Confident",
            "Young adult woman with a confident and warm, mature quality and a reassuring, professional tone.",
        ),
        (
            "bIHbv24MWmeRgasZH58o",
            "Will - Relaxed Optimist",
            "Conversational and laid back.",
        ),
    ]
]

__all__ = ["ELEVENLABS_VOICES"]
