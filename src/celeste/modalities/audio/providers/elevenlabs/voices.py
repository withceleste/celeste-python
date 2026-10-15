"""ElevenLabs voice definitions for audio modality."""

from celeste.core import Provider

from ...voices import Voice

# Snapshot 2026-10-15: 19 default voice replacements from GET /v1/shared-voices.
# Source: https://elevenlabs.io/docs/help-center/product/voices/my-voices/what-are-default-voices
ELEVENLABS_VOICES = [
    Voice(
        id=voice_id,
        provider=Provider.ELEVENLABS,
        name=name,
        description=description,
    )
    for voice_id, name, description in [
        (
            "BFd5oBc2DDna33pSi4Gf",
            "Alicia - Polished Global Anchor",
            "Authoritative, refined British female RP. Impeccable diction and a sophisticated tone ideal for corporate narration and prestige news.",
        ),
        (
            "jSuBIjxMKhqIfb0wCK1F",
            "Baxter - Dry Calm Aussie",
            "Medium low male tone with an Australian/New Zealand accent. Grounded and steady for documentary style narration.",
        ),
        (
            "AaOhDHYJ1XLZk74lXhdE",
            "Caleb - Trusted Guide",
            'Down-to-earth with a slight smile in the tone. It\u2019s a grounded, mid-range voice that works perfectly for "slice of life" stories or relatable brand messaging.',
        ),
        (
            "gOupLcAkjEnguROwi4oS",
            "Darian - Warm Grounded Storyteller",
            "Warm, grounded male baritone. Natural and confident for storytelling and brand reads.",
        ),
        (
            "l7kNoIfnJKPg7779LI2t",
            "Eddie - Natural and Helpful",
            "Clear, melodic male tenor. Patient and exceptionally polite, designed for instructional IVR systems and supportive customer-facing tutorials.",
        ),
        (
            "WQP7cQUF5aAS6Axh5yaa",
            "Elara - Crisp Pro Narrator",
            "Clean, bright female tone. Polished and clear for professional narration and product demos.",
        ),
        (
            "6WwXjDDEMyNmFG95zycZ",
            "Eldrin - Crisp British Baritone",
            "Gritty mid range baritone with a modern British accent. Clear, controlled, and trustworthy for narration and explainers.",
        ),
        (
            "dvbL7qkNGZY1IqPGZAjM",
            "Elowen - Upbeat Modern Narrator",
            "Bright, smooth female tone. Young and lively, with clear diction for modern narration and promos.",
        ),
        (
            "fnYMz3F5gMEDGMWcH1ex",
            "Finley -  Articulate Anchor",
            "Crisp, clear, and unflappable. This rhythmic British voice provides a sense of authority and flow for complex explainers.",
        ),
        (
            "22N9cF8z0o7y23njdyaY",
            "Florence - Atmospheric Storyteller",
            "Sophisticated and lyrical, this voice flows like a steady stream. Perfect for immersive audiobooks or historical documentaries where the tone needs to be both grand and intimate.",
        ),
        (
            "g7LVvkPWALzPxOQbF6OE",
            "Jade - Upbeat and Natural",
            'High-energy, unpredictable female voice. Features rapid-fire delivery and a playful, erratic cadence for "Gen-Z" marketing and avant-garde media.',
        ),
        (
            "10NkTYmU7tSz3Kkl3Lex",
            "Kaelen - Amateur Warrior",
            "Rugged, gravelly male bass-baritone. Intense and textured, perfect for cinematic trailers or hardened character monologues.",
        ),
        (
            "ktkP7Nsj67dw2zcplQYt",
            "Lawrence - Bright and Informative",
            "Crisp, energetic male with a resonant tone. Articulate and engaging for educational content and high-energy commercial voiceovers.",
        ),
        (
            "QtY3JBOUKEB5xzrRfOKc",
            "Maisie - Friendly Casual Neighbor",
            'Warm, approachable female alto. Bright and unpretentious for "girl-next-door" commercials and relatable social media content.',
        ),
        (
            "8dEUmyPMdDdK91vboYih",
            "Sawyer - Midnight Storyteller",
            "A rich, gravelly baritone with a steady pulse. Perfect for cinematic trailers, noir narrations, or premium luxury advertisements.",
        ),
        (
            "OZ0L6eISlOejga3XjDFt",
            "Talia - Warm Soft Guide",
            "Warm female tone. Soft, caring, and relaxed for calm narration and supportive messages.",
        ),
        (
            "cymHWdiF8WjUCg6vvFxx",
            "Vane - Rugged and gravelly",
            "A weathered voice with a sharp edge. It carries a sense of lived-in fatigue and cynicism, perfect for a world-weary anti-hero or a shadowed figure in a noir setting.",
        ),
        (
            "7QN34D2r3hCNwbOYIeK0",
            "Warren - Effortless and Cool",
            "Smooth, laid-back male baritone. Relaxed pacing and a modern, conversational flow for lifestyle brands and authentic storytelling.",
        ),
        (
            "FrS6cKLB1wg4WYgPa9GW",
            "Wyatt - Seasoned Mentor",
            "Measured and thoughtful, this voice carries the weight of experience. Ideal for long-form documentaries or insightful educational content.",
        ),
    ]
]

__all__ = ["ELEVENLABS_VOICES"]
