# Mureka Music Generation - Celeste AI Integration

This document describes how to use the Mureka provider in Celeste AI for music generation and related features.

## Overview

Mureka is a comprehensive music generation platform that allows you to:
- Generate songs with vocals and lyrics
- Generate instrumental music
- Create, extend, and manipulate lyrics
- Extend existing songs
- Analyze song characteristics
- Separate audio tracks (stemming)

## Getting Started

### Installation

```bash
pip install "celeste-ai[music-generation]"
```

### Setup

Set your Mureka API key as an environment variable:

```bash
export MUREKA_API_KEY="your-api-key-here"
```

Or use a `.env` file:

```bash
MUREKA_API_KEY=your-api-key-here
```

## Basic Usage

### Generate a Song with Lyrics

```python
import asyncio
from celeste import Capability, Provider, create_client

async def main():
    # Create client
    client = create_client(
        capability=Capability.MUSIC_GENERATION,
        provider=Provider.MUREKA,
    )

    # Generate song
    response = await client.generate(
        prompt="upbeat pop song with energetic vibes",
        lyrics="[Verse]\nSummer days and endless nights\nChasing dreams under starlit skies",
    )

    print(f"Song URL: {response.content.url}")
    print(f"Model used: {response.metadata['model']}")

asyncio.run(main())
```

### Generate Instrumental Music

```python
# Generate instrumental only (no vocals)
response = await client.generate(
    prompt="epic orchestral soundtrack with dramatic crescendos",
    instrumental_only=True,
)
```

## Available Models

Mureka provides several models for music generation:

| Model ID | Description | Streaming | Max Duration |
|----------|-------------|-----------|--------------|
| `auto` | Latest regular model (recommended) | ✅ | 600s |
| `mureka-6` | Model v6 | ✅ | 600s |
| `mureka-7.5` | Model v7.5 | ✅ | 600s |
| `mureka-o1` | Advanced model | ❌ | 180s |

```python
# Specify a model explicitly
client = create_client(
    capability=Capability.MUSIC_GENERATION,
    provider=Provider.MUREKA,
    model="mureka-7.5",
)
```

## Advanced Features

### 1. Generate Lyrics

Create lyrics from a theme or description:

```python
lyrics_output = await client.generate_lyrics(
    prompt="A song about summer adventures and friendship"
)

print(f"Title: {lyrics_output.title}")
print(f"Lyrics:\n{lyrics_output.lyrics}")
```

### 2. Extend Lyrics

Continue existing lyrics:

```python
existing_lyrics = """[Verse]
In the stormy night, I wander alone
Lost in the rain"""

extended = await client.extend_lyrics(lyrics=existing_lyrics)
print(f"Extended lyrics:\n{extended.lyrics}")
```

### 3. Extend a Song

Add more content to an existing song:

```python
# Using a song ID from a previous generation
extended_song = await client.extend_song(
    song_id="109676802932737",  # From response.metadata['task_id']
    lyrics="[Chorus]\nAnd the music plays on",
    extend_at=30000,  # Start at 30 seconds (in milliseconds)
)

# Or using an uploaded audio file
extended_song = await client.extend_song(
    upload_audio_id="your-upload-id",
    lyrics="[Bridge]\nHere we go again",
    extend_at=60000,  # Start at 60 seconds
)
```

**Note:** `extend_at` must be between 8000ms (8s) and 420000ms (7min).

### 4. Describe a Song

Analyze a song's characteristics:

```python
description = await client.describe_song(
    url="https://example.com/song.mp3"
)

print(f"Instruments: {', '.join(description.instruments)}")
print(f"Genres: {', '.join(description.genres)}")
print(f"Tags: {', '.join(description.tags)}")
print(f"Description: {description.description}")
```

You can also use base64-encoded audio:

```python
import base64

with open("song.mp3", "rb") as f:
    audio_data = base64.b64encode(f.read()).decode()

description = await client.describe_song(
    url=f"data:audio/mp3;base64,{audio_data}"
)
```

### 5. Stem a Song (Track Separation)

Separate a song into individual tracks:

```python
stem_output = await client.stem_song(
    url="https://example.com/song.mp3"
)

print(f"Download stems from: {stem_output.zip_url}")
print(f"Link expires at: {stem_output.expires_at}")

# Download the ZIP file
import httpx
async with httpx.AsyncClient() as http:
    zip_response = await http.get(stem_output.zip_url)
    with open("stems.zip", "wb") as f:
        f.write(zip_response.content)
```

### 6. Check Billing Information

Get your account balance and usage:

```python
billing = await client.get_billing()

print(f"Account ID: {billing.account_id}")
print(f"Balance: ${billing.balance / 100:.2f}")
print(f"Total spending: ${billing.total_spending / 100:.2f}")
print(f"Concurrent request limit: {billing.concurrent_request_limit}")
```

## Parameters

### Song Generation Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `prompt` | str | Style description (e.g., "r&b, slow, passionate") |
| `lyrics` | str | Song lyrics (required for songs) |
| `n` | int | Number of outputs (1-3, default: 2) |
| `stream` | bool | Enable streaming playback during generation |
| `instrumental_only` | bool | Generate instrumental without vocals |

### Reference Parameters

You can control generation using uploaded reference files:

| Parameter | Type | Description |
|-----------|------|-------------|
| `reference_id` | str | Reference music file (mutually exclusive with prompt) |
| `vocal_id` | str | Custom voice reference |
| `melody_id` | str | Melody reference (mutually exclusive with reference_id) |
| `instrumental_id` | str | Instrumental reference (for instrumental generation) |

**Note:** When using `prompt`, don't use `reference_id`, `vocal_id`, or `melody_id`.

## Response Objects

### MusicGenerationOutput

```python
response = await client.generate(...)

# Audio content
response.content.url  # str: URL to download/stream

# Metadata
response.metadata["task_id"]  # str: Task ID for future reference
response.metadata["trace_id"]  # str: For debugging
response.metadata["model"]  # str: Model used

# Usage (if available)
response.usage.credits_used  # float: Credits consumed
response.usage.total_tokens  # int: Tokens used

# Completion status
response.finish_reason.reason  # str: "succeeded", "failed", etc.
```

### LyricsOutput

```python
lyrics = await client.generate_lyrics(...)

lyrics.title  # str | None: Generated title
lyrics.lyrics  # str: Generated lyrics
```

### SongDescription

```python
desc = await client.describe_song(...)

desc.instruments  # list[str]: Detected instruments
desc.genres  # list[str]: Music genres
desc.tags  # list[str]: Tags/keywords
desc.description  # str: Overall description
```

### StemOutput

```python
stems = await client.stem_song(...)

stems.zip_url  # str: URL to download stems ZIP
stems.expires_at  # int: Unix timestamp when URL expires
```

### BillingInfo

```python
billing = await client.get_billing()

billing.account_id  # int
billing.balance  # int: Balance in cents
billing.total_recharge  # int: Total recharged in cents
billing.total_spending  # int: Total spent in cents
billing.concurrent_request_limit  # int: Max concurrent requests
```

## Error Handling

Celeste provides specific exception types for Mureka errors:

```python
from celeste_music_generation.providers.mureka.exceptions import (
    MurekaInvalidRequestError,  # 400
    MurekaAuthenticationError,  # 401
    MurekaForbiddenError,  # 403
    MurekaRateLimitError,  # 429
    MurekaQuotaExceededError,  # 429 (out of credits)
    MurekaServerError,  # 500
    MurekaOverloadedError,  # 503
)

try:
    response = await client.generate(...)
except MurekaRateLimitError as e:
    print(f"Rate limited: {e.message}")
    print(f"Trace ID: {e.trace_id}")
except MurekaQuotaExceededError:
    print("Out of credits - please recharge")
except MurekaInvalidRequestError as e:
    print(f"Invalid request: {e.message}")
```

## Best Practices

### 1. Prompt Engineering

For best results with the `prompt` parameter:

```python
# Good: Descriptive style attributes
prompt="r&b, slow tempo, passionate male vocal, piano-driven"

# Good: Genre + mood + instruments
prompt="indie folk, melancholic, acoustic guitar and soft vocals"

# Less effective: Story/lyrics in prompt
prompt="a song about love"  # Use lyrics parameter instead
```

### 2. Lyrics Format

Structure your lyrics with sections for better results:

```python
lyrics="""[Verse]
Walking down the street
Feeling the summer heat

[Chorus]
This is where we belong
Singing our favorite song

[Verse]
Memories fade away
But the music will stay
"""
```

### 3. Resource Management

```python
# Use async context manager for automatic cleanup
from celeste import create_client

async with create_client(
    capability=Capability.MUSIC_GENERATION,
    provider=Provider.MUREKA,
) as client:
    response = await client.generate(...)
    # Client automatically closed after block
```

### 4. Handling Long Generations

Music generation can take time. Monitor progress:

```python
import asyncio

async def generate_with_progress():
    print("Starting generation...")

    # Generation happens in background with polling
    response = await client.generate(
        prompt="epic soundtrack",
        lyrics="...",
    )

    print("Generation complete!")
    return response

# The client handles polling automatically
result = await generate_with_progress()
```

### 5. Batch Operations

Generate multiple variations:

```python
# Request multiple outputs at once
response = await client.generate(
    prompt="upbeat electronic",
    lyrics="...",
    n=3,  # Generate 3 variations
)

# Access via response.metadata or choices (check response structure)
```

## Limitations

- **Lyrics length**: Maximum 3000 characters
- **Prompt length**: Maximum 1024 characters
- **Song duration**:
  - Regular models: 5-600 seconds
  - mureka-o1: 5-180 seconds
- **Extend range**: 8-420 seconds
- **Concurrent requests**: Check your account limits with `get_billing()`
- **File uploads**: Max 10MB for base64 data URLs
- **Streaming**: Not available with mureka-o1 model

## API Endpoints

Celeste abstracts these, but for reference:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/song/generate` | POST | Generate song with vocals |
| `/v1/instrumental/generate` | POST | Generate instrumental |
| `/v1/lyrics/generate` | POST | Generate lyrics |
| `/v1/lyrics/extend` | POST | Extend lyrics |
| `/v1/song/extend` | POST | Extend song |
| `/v1/song/describe` | POST | Analyze song |
| `/v1/song/stem` | POST | Separate tracks |
| `/v1/account/billing` | GET | Get billing info |

## Support

For issues or questions:
- [Celeste AI GitHub](https://github.com/anthropics/celeste-python)
- [Mureka Platform](https://platform.mureka.ai)

## Examples

Find complete examples in the `examples/` directory:
- `music_generation_example.py` - Basic song generation
- `mureka_advanced_example.py` - All Mureka features (coming soon)
