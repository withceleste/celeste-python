"""Example: Music generation with Mureka provider.

This example demonstrates how to use Celeste AI to generate music using the Mureka provider.

Setup:
    1. Install: uv add "celeste-ai[music-generation]"
    2. Set environment variable: MUREKA_API_KEY=your-api-key
    3. Run: uv run python examples/music_generation_example.py
"""

import asyncio

from celeste import Capability, Provider, create_client


async def basic_music_generation() -> None:
    """Generate music with a simple prompt."""
    print("🎵 Basic Music Generation Example\n")

    # Create client
    client = create_client(
        capability=Capability.MUSIC_GENERATION,
        provider=Provider.MUREKA,
    )

    # Generate music
    print("Generating upbeat electronic music...")
    response = await client.generate(
        prompt="Upbeat electronic music with a driving beat",
    )

    print(f"✓ Music generated!")
    print(f"  URL: {response.content.url}")
    print(f"  Task ID: {response.metadata.get('task_id')}")
    print(f"  Trace ID: {response.metadata.get('trace_id')}\n")


async def music_with_lyrics() -> None:
    """Generate a song with custom lyrics."""
    print("🎤 Music Generation with Lyrics Example\n")

    client = create_client(
        capability=Capability.MUSIC_GENERATION,
        provider=Provider.MUREKA,
    )

    # Generate song with lyrics
    print("Generating pop song with lyrics...")
    response = await client.generate(
        prompt="Cheerful pop song about summer adventures",
        lyrics="Summer days and endless nights\nChasing dreams under starlit skies",
    )

    print(f"✓ Song generated!")
    print(f"  URL: {response.content.url}")
    print(f"  Duration: {response.metadata.get('duration')}s\n")


async def instrumental_music() -> None:
    """Generate instrumental music only."""
    print("🎼 Instrumental Music Generation Example\n")

    client = create_client(
        capability=Capability.MUSIC_GENERATION,
        provider=Provider.MUREKA,
    )

    # Generate instrumental
    print("Generating orchestral soundtrack...")
    response = await client.generate(
        prompt="Epic orchestral soundtrack with dramatic crescendos",
        instrumental_only=True,
    )

    print(f"✓ Instrumental generated!")
    print(f"  URL: {response.content.url}\n")


async def music_with_parameters() -> None:
    """Generate music with advanced parameters."""
    print("🎹 Advanced Parameters Example\n")

    client = create_client(
        capability=Capability.MUSIC_GENERATION,
        provider=Provider.MUREKA,
        model="mureka-7.5",  # Specify model explicitly
    )

    # Generate with detailed parameters
    print("Generating jazz fusion track...")
    response = await client.generate(
        prompt="Smooth jazz fusion with piano and saxophone",
    )

    print(f"✓ Jazz track generated!")
    print(f"  URL: {response.content.url}")
    print(f"  Model: {client.model.id}")
    print(f"  Quality: high\n")


async def generate_and_extend_lyrics() -> None:
    """Generate and extend lyrics."""
    print("📝 Lyrics Generation Example\n")

    client = create_client(
        capability=Capability.MUSIC_GENERATION,
        provider=Provider.MUREKA,
    )

    # Generate lyrics
    print("Generating lyrics...")
    lyrics_output = await client.generate_lyrics(
        prompt="A song about summer adventures and friendship"
    )

    print(f"✓ Lyrics generated!")
    print(f"  Title: {lyrics_output.title}")
    print(f"  Lyrics preview: {lyrics_output.lyrics[:100]}...")
    print()

    # Extend lyrics
    print("Extending lyrics...")
    extended = await client.extend_lyrics(lyrics=lyrics_output.lyrics)

    print(f"✓ Lyrics extended!")
    print(f"  Extended length: {len(extended.lyrics)} characters\n")


async def analyze_song() -> None:
    """Describe a song's characteristics."""
    print("🔍 Song Analysis Example\n")

    client = create_client(
        capability=Capability.MUSIC_GENERATION,
        provider=Provider.MUREKA,
    )

    # Note: You would use a real song URL here
    # For demo purposes, this example is commented out
    print("Example: Analyze a song (requires a real song URL)")
    print("Code:")
    print("  description = await client.describe_song(")
    print("      url='https://example.com/song.mp3'")
    print("  )")
    print("  print(f'Instruments: {description.instruments}')")
    print("  print(f'Genres: {description.genres}')\n")


async def check_billing() -> None:
    """Check account billing information."""
    print("💰 Billing Information Example\n")

    client = create_client(
        capability=Capability.MUSIC_GENERATION,
        provider=Provider.MUREKA,
    )

    print("Fetching billing information...")
    billing = await client.get_billing()

    print(f"✓ Billing info retrieved!")
    print(f"  Account ID: {billing.account_id}")
    print(f"  Balance: ${billing.balance / 100:.2f}")
    print(f"  Total spending: ${billing.total_spending / 100:.2f}")
    print(f"  Concurrent limit: {billing.concurrent_request_limit}\n")


async def main() -> None:
    """Run all examples."""
    print("=" * 60)
    print("Celeste AI - Music Generation Examples")
    print("=" * 60)
    print()

    try:
        # Run examples
        await basic_music_generation()
        await music_with_lyrics()
        await instrumental_music()
        await music_with_parameters()
        await generate_and_extend_lyrics()
        await analyze_song()
        await check_billing()

        print("=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("  1. Installed: uv add 'celeste-ai[music-generation]'")
        print("  2. Set environment variable: MUREKA_API_KEY=your-api-key")


if __name__ == "__main__":
    asyncio.run(main())
