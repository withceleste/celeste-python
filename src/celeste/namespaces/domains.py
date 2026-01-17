"""Domain-specific namespaces for Celeste SDK.

Each namespace provides methods for operations on a specific domain (resource type).
The namespace routes to the appropriate modality client based on the operation.
"""

from typing import Any, Unpack

from pydantic import SecretStr

from celeste import create_client
from celeste.artifacts import ImageArtifact
from celeste.core import Modality, Operation, Provider
from celeste.modalities.audio.io import AudioOutput
from celeste.modalities.audio.parameters import AudioParameters
from celeste.modalities.audio.streaming import AudioStream
from celeste.modalities.embeddings.io import EmbeddingsOutput
from celeste.modalities.embeddings.parameters import EmbeddingsParameters
from celeste.modalities.images.io import ImageOutput
from celeste.modalities.images.parameters import ImageParameters
from celeste.modalities.images.streaming import ImagesStream
from celeste.modalities.text.io import TextInput, TextOutput
from celeste.modalities.text.parameters import TextParameters
from celeste.modalities.text.streaming import TextStream
from celeste.modalities.videos.io import VideoOutput
from celeste.modalities.videos.parameters import VideoParameters
from celeste.types import AudioContent, ImageContent, Message, VideoContent


class SyncStreamTextNamespace:
    """celeste.text.sync.stream.* namespace."""

    def generate(
        self,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        base_url: str | None = None,
        extra_body: dict[str, Any] | None = None,
        **params: Unpack[TextParameters],
    ) -> TextStream:
        """Sync streaming text generation."""
        client = create_client(
            modality=Modality.TEXT,
            operation=Operation.GENERATE,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return client.sync.stream.generate(
            prompt,
            messages=messages,
            base_url=base_url,
            extra_body=extra_body,
            **params,
        )


class StreamTextNamespace:
    """celeste.text.stream.* namespace."""

    def generate(
        self,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        base_url: str | None = None,
        extra_body: dict[str, Any] | None = None,
        **params: Unpack[TextParameters],
    ) -> TextStream:
        """Async streaming text generation."""
        client = create_client(
            modality=Modality.TEXT,
            operation=Operation.GENERATE,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return client.stream.generate(
            prompt,
            messages=messages,
            base_url=base_url,
            extra_body=extra_body,
            **params,
        )


class SyncTextNamespace:
    """celeste.text.sync.* namespace."""

    def generate(
        self,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        base_url: str | None = None,
        extra_body: dict[str, Any] | None = None,
        **params: Unpack[TextParameters],
    ) -> TextOutput:
        """Blocking text generation."""
        client = create_client(
            modality=Modality.TEXT,
            operation=Operation.GENERATE,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return client.sync.generate(
            prompt,
            messages=messages,
            base_url=base_url,
            extra_body=extra_body,
            **params,
        )

    def embed(
        self,
        text: str | list[str],
        *,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        **params: Unpack[EmbeddingsParameters],
    ) -> EmbeddingsOutput:
        """Blocking embeddings generation."""
        client = create_client(
            modality=Modality.EMBEDDINGS,
            operation=Operation.EMBED,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return client.sync.embed(text, **params)

    @property
    def stream(self) -> SyncStreamTextNamespace:
        """Access sync streaming text operations."""
        return SyncStreamTextNamespace()


class TextNamespace:
    """celeste.text.* namespace.

    Provides text generation and embedding operations.
    """

    async def generate(
        self,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        base_url: str | None = None,
        extra_body: dict[str, Any] | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextOutput:
        """Generate text from a prompt.

        Args:
            prompt: The text prompt for generation.
            messages: List of messages for multi-turn conversations.
            model: Model ID to use (required).
            provider: Optional provider override.
            api_key: Optional API key override.
            base_url: Optional base URL for OpenResponses providers.
            extra_body: Optional provider-specific request body fields.
            **parameters: Additional model parameters.

        Returns:
            TextOutput with generated text.
        """
        client = create_client(
            modality=Modality.TEXT,
            operation=Operation.GENERATE,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        inputs = TextInput(prompt=prompt, messages=messages)
        return await client._predict(
            inputs, base_url=base_url, extra_body=extra_body, **parameters
        )

    async def embed(
        self,
        text: str | list[str],
        *,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        **parameters: Unpack[EmbeddingsParameters],
    ) -> EmbeddingsOutput:
        """Generate embeddings from text.

        Args:
            text: Text to embed. Single string or list of strings.
            model: Model ID to use (required).
            provider: Optional provider override.
            api_key: Optional API key override.
            **parameters: Additional model parameters.

        Returns:
            EmbeddingsOutput with embedding vectors.
        """
        client = create_client(
            modality=Modality.EMBEDDINGS,
            operation=Operation.EMBED,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return await client.embed(text, **parameters)

    @property
    def sync(self) -> SyncTextNamespace:
        """Access synchronous text operations."""
        return SyncTextNamespace()

    @property
    def stream(self) -> StreamTextNamespace:
        """Access streaming text operations."""
        return StreamTextNamespace()


class SyncStreamImagesNamespace:
    """celeste.images.sync.stream.* namespace."""

    def generate(
        self,
        prompt: str,
        *,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        **params: Unpack[ImageParameters],
    ) -> ImagesStream:
        """Sync streaming image generation."""
        client = create_client(
            modality=Modality.IMAGES,
            operation=Operation.GENERATE,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return client.sync.stream.generate(prompt, **params)

    def edit(
        self,
        image: ImageArtifact,
        prompt: str,
        *,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        **params: Unpack[ImageParameters],
    ) -> ImagesStream:
        """Sync streaming image editing."""
        client = create_client(
            modality=Modality.IMAGES,
            operation=Operation.EDIT,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return client.sync.stream.edit(image, prompt, **params)

    def analyze(
        self,
        image: ImageContent,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        **params: Unpack[TextParameters],
    ) -> TextStream:
        """Sync streaming image analysis."""
        client = create_client(
            modality=Modality.TEXT,
            operation=Operation.ANALYZE,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return client.sync.stream.analyze(
            prompt, messages=messages, image=image, **params
        )


class StreamImagesNamespace:
    """celeste.images.stream.* namespace."""

    def generate(
        self,
        prompt: str,
        *,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        **params: Unpack[ImageParameters],
    ) -> ImagesStream:
        """Async streaming image generation."""
        client = create_client(
            modality=Modality.IMAGES,
            operation=Operation.GENERATE,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return client.stream.generate(prompt, **params)

    def edit(
        self,
        image: ImageArtifact,
        prompt: str,
        *,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        **params: Unpack[ImageParameters],
    ) -> ImagesStream:
        """Async streaming image editing."""
        client = create_client(
            modality=Modality.IMAGES,
            operation=Operation.EDIT,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return client.stream.edit(image, prompt, **params)

    def analyze(
        self,
        image: ImageContent,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        **params: Unpack[TextParameters],
    ) -> TextStream:
        """Async streaming image analysis."""
        client = create_client(
            modality=Modality.TEXT,
            operation=Operation.ANALYZE,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return client.stream.analyze(prompt, messages=messages, image=image, **params)


class SyncImagesNamespace:
    """celeste.images.sync.* namespace."""

    def generate(
        self,
        prompt: str,
        *,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        **params: Unpack[ImageParameters],
    ) -> ImageOutput:
        """Blocking image generation."""
        client = create_client(
            modality=Modality.IMAGES,
            operation=Operation.GENERATE,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return client.sync.generate(prompt, **params)

    def edit(
        self,
        image: ImageArtifact,
        prompt: str,
        *,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        **params: Unpack[ImageParameters],
    ) -> ImageOutput:
        """Blocking image editing."""
        client = create_client(
            modality=Modality.IMAGES,
            operation=Operation.EDIT,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return client.sync.edit(image, prompt, **params)

    def analyze(
        self,
        image: ImageContent,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        **params: Unpack[TextParameters],
    ) -> TextOutput:
        """Blocking image analysis."""
        client = create_client(
            modality=Modality.TEXT,
            operation=Operation.ANALYZE,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return client.sync.analyze(prompt, messages=messages, image=image, **params)

    @property
    def stream(self) -> SyncStreamImagesNamespace:
        """Access sync streaming image operations."""
        return SyncStreamImagesNamespace()


class ImagesNamespace:
    """celeste.images.* namespace.

    Provides image generation, editing, and analysis operations.
    """

    async def generate(
        self,
        prompt: str,
        *,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        **parameters: Unpack[ImageParameters],
    ) -> ImageOutput:
        """Generate images from a prompt.

        Args:
            prompt: The text prompt for image generation.
            model: Model ID to use (required).
            provider: Optional provider override.
            api_key: Optional API key override.
            **parameters: Additional model parameters.

        Returns:
            ImageOutput with generated image.
        """
        client = create_client(
            modality=Modality.IMAGES,
            operation=Operation.GENERATE,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return await client.generate(prompt, **parameters)

    async def edit(
        self,
        image: ImageArtifact,
        prompt: str,
        *,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        **parameters: Unpack[ImageParameters],
    ) -> ImageOutput:
        """Edit an image with a prompt.

        Args:
            image: The image to edit.
            prompt: Instructions for editing.
            model: Model ID to use (required).
            provider: Optional provider override.
            api_key: Optional API key override.
            **parameters: Additional model parameters.

        Returns:
            ImageOutput with edited image.
        """
        client = create_client(
            modality=Modality.IMAGES,
            operation=Operation.EDIT,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return await client.edit(image, prompt, **parameters)

    async def analyze(
        self,
        image: ImageContent,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextOutput:
        """Analyze images and return text description.

        Args:
            image: Image or list of images to analyze.
            prompt: Question or instruction about the image.
            messages: List of messages for multi-turn conversations.
            model: Model ID to use (required).
            provider: Optional provider override.
            api_key: Optional API key override.
            **parameters: Additional model parameters.

        Returns:
            TextOutput with analysis result.
        """
        client = create_client(
            modality=Modality.TEXT,
            operation=Operation.ANALYZE,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return await client.analyze(
            prompt, messages=messages, image=image, **parameters
        )

    @property
    def sync(self) -> SyncImagesNamespace:
        """Access synchronous image operations."""
        return SyncImagesNamespace()

    @property
    def stream(self) -> StreamImagesNamespace:
        """Access streaming image operations."""
        return StreamImagesNamespace()


class SyncStreamAudioNamespace:
    """celeste.audio.sync.stream.* namespace."""

    def speak(
        self,
        text: str,
        *,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        **params: Unpack[AudioParameters],
    ) -> AudioStream:
        """Sync streaming text-to-speech."""
        client = create_client(
            modality=Modality.AUDIO,
            operation=Operation.SPEAK,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return client.sync.stream.speak(text, **params)

    def analyze(
        self,
        audio: AudioContent,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        **params: Unpack[TextParameters],
    ) -> TextStream:
        """Sync streaming audio analysis."""
        client = create_client(
            modality=Modality.TEXT,
            operation=Operation.ANALYZE,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return client.sync.stream.analyze(
            prompt, messages=messages, audio=audio, **params
        )


class StreamAudioNamespace:
    """celeste.audio.stream.* namespace."""

    def speak(
        self,
        text: str,
        *,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        **params: Unpack[AudioParameters],
    ) -> AudioStream:
        """Async streaming text-to-speech."""
        client = create_client(
            modality=Modality.AUDIO,
            operation=Operation.SPEAK,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return client.stream.speak(text, **params)

    def analyze(
        self,
        audio: AudioContent,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        **params: Unpack[TextParameters],
    ) -> TextStream:
        """Async streaming audio analysis."""
        client = create_client(
            modality=Modality.TEXT,
            operation=Operation.ANALYZE,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return client.stream.analyze(prompt, messages=messages, audio=audio, **params)


class SyncAudioNamespace:
    """celeste.audio.sync.* namespace."""

    def speak(
        self,
        text: str,
        *,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        **params: Unpack[AudioParameters],
    ) -> AudioOutput:
        """Blocking text-to-speech."""
        client = create_client(
            modality=Modality.AUDIO,
            operation=Operation.SPEAK,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return client.sync.speak(text, **params)

    def analyze(
        self,
        audio: AudioContent,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        **params: Unpack[TextParameters],
    ) -> TextOutput:
        """Blocking audio analysis."""
        client = create_client(
            modality=Modality.TEXT,
            operation=Operation.ANALYZE,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return client.sync.analyze(prompt, messages=messages, audio=audio, **params)

    @property
    def stream(self) -> SyncStreamAudioNamespace:
        """Access sync streaming audio operations."""
        return SyncStreamAudioNamespace()


class AudioNamespace:
    """celeste.audio.* namespace.

    Provides text-to-speech and audio analysis operations.
    """

    async def speak(
        self,
        text: str,
        *,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        **parameters: Unpack[AudioParameters],
    ) -> AudioOutput:
        """Convert text to speech.

        Args:
            text: Text to convert to speech.
            model: Model ID to use (required).
            provider: Optional provider override.
            api_key: Optional API key override.
            **parameters: Additional model parameters (e.g., voice).

        Returns:
            AudioOutput with generated audio.
        """
        client = create_client(
            modality=Modality.AUDIO,
            operation=Operation.SPEAK,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return await client.speak(text, **parameters)

    async def analyze(
        self,
        audio: AudioContent,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextOutput:
        """Analyze audio and return text transcription/description.

        Args:
            audio: Audio or list of audio files to analyze.
            prompt: Question or instruction about the audio.
            messages: List of messages for multi-turn conversations.
            model: Model ID to use (required).
            provider: Optional provider override.
            api_key: Optional API key override.
            **parameters: Additional model parameters.

        Returns:
            TextOutput with analysis/transcription result.
        """
        client = create_client(
            modality=Modality.TEXT,
            operation=Operation.ANALYZE,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return await client.analyze(
            prompt, messages=messages, audio=audio, **parameters
        )

    @property
    def sync(self) -> SyncAudioNamespace:
        """Access synchronous audio operations."""
        return SyncAudioNamespace()

    @property
    def stream(self) -> StreamAudioNamespace:
        """Access streaming audio operations."""
        return StreamAudioNamespace()


class SyncStreamVideosNamespace:
    """celeste.videos.sync.stream.* namespace."""

    def analyze(
        self,
        video: VideoContent,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        **params: Unpack[TextParameters],
    ) -> TextStream:
        """Sync streaming video analysis."""
        client = create_client(
            modality=Modality.TEXT,
            operation=Operation.ANALYZE,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return client.sync.stream.analyze(
            prompt, messages=messages, video=video, **params
        )


class StreamVideosNamespace:
    """celeste.videos.stream.* namespace."""

    def analyze(
        self,
        video: VideoContent,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        **params: Unpack[TextParameters],
    ) -> TextStream:
        """Async streaming video analysis."""
        client = create_client(
            modality=Modality.TEXT,
            operation=Operation.ANALYZE,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return client.stream.analyze(prompt, messages=messages, video=video, **params)


class SyncVideosNamespace:
    """celeste.videos.sync.* namespace."""

    def generate(
        self,
        prompt: str,
        *,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        **params: Unpack[VideoParameters],
    ) -> VideoOutput:
        """Blocking video generation."""
        client = create_client(
            modality=Modality.VIDEOS,
            operation=Operation.GENERATE,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return client.sync.generate(prompt, **params)

    def analyze(
        self,
        video: VideoContent,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        **params: Unpack[TextParameters],
    ) -> TextOutput:
        """Blocking video analysis."""
        client = create_client(
            modality=Modality.TEXT,
            operation=Operation.ANALYZE,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return client.sync.analyze(prompt, messages=messages, video=video, **params)

    @property
    def stream(self) -> SyncStreamVideosNamespace:
        """Access sync streaming video operations."""
        return SyncStreamVideosNamespace()


class VideosNamespace:
    """celeste.videos.* namespace.

    Provides video generation and analysis operations.
    """

    async def generate(
        self,
        prompt: str,
        *,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        **parameters: Unpack[VideoParameters],
    ) -> VideoOutput:
        """Generate video from a prompt.

        Args:
            prompt: The text prompt for video generation.
            model: Model ID to use (required).
            provider: Optional provider override.
            api_key: Optional API key override.
            **parameters: Additional model parameters.

        Returns:
            VideoOutput with generated video.
        """
        client = create_client(
            modality=Modality.VIDEOS,
            operation=Operation.GENERATE,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return await client.generate(prompt, **parameters)

    async def analyze(
        self,
        video: VideoContent,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        model: str,
        provider: Provider | None = None,
        api_key: str | SecretStr | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextOutput:
        """Analyze video and return text description.

        Args:
            video: Video or list of videos to analyze.
            prompt: Question or instruction about the video.
            messages: List of messages for multi-turn conversations.
            model: Model ID to use (required).
            provider: Optional provider override.
            api_key: Optional API key override.
            **parameters: Additional model parameters.

        Returns:
            TextOutput with analysis result.
        """
        client = create_client(
            modality=Modality.TEXT,
            operation=Operation.ANALYZE,
            model=model,
            provider=provider,
            api_key=api_key,
        )
        return await client.analyze(
            prompt, messages=messages, video=video, **parameters
        )

    @property
    def sync(self) -> SyncVideosNamespace:
        """Access synchronous video operations."""
        return SyncVideosNamespace()

    @property
    def stream(self) -> StreamVideosNamespace:
        """Access streaming video operations."""
        return StreamVideosNamespace()


__all__ = [
    "AudioNamespace",
    "ImagesNamespace",
    "TextNamespace",
    "VideosNamespace",
]
