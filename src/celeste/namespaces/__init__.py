"""Domain namespace API for Celeste SDK.

Provides domain-first interface for AI operations:

    import celeste

    # Async (default)
    result = await celeste.text.generate("Hello", model="gpt-4o")

    # Sync
    result = celeste.text.sync.generate("Hello", model="gpt-4o")

    # Async streaming
    async for chunk in celeste.text.stream.generate("Hello", model="gpt-4o"):
        print(chunk.content, end="")

    # Sync streaming
    for chunk in celeste.text.sync.stream.generate("Hello", model="gpt-4o"):
        print(chunk.content, end="")
"""

from celeste.namespaces.domains import (
    AudioNamespace,
    DocumentsNamespace,
    ImagesNamespace,
    LiveNamespace,
    TextNamespace,
    VideosNamespace,
)

# Module-level singletons
text = TextNamespace()
images = ImagesNamespace()
audio = AudioNamespace()
videos = VideosNamespace()
documents = DocumentsNamespace()
live = LiveNamespace()

__all__ = [
    "AudioNamespace",
    "DocumentsNamespace",
    "ImagesNamespace",
    "LiveNamespace",
    "TextNamespace",
    "VideosNamespace",
    "audio",
    "documents",
    "images",
    "live",
    "text",
    "videos",
]
