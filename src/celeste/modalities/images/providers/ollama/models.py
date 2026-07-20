"""Ollama models for images modality."""

from celeste.models import Model

# Dynamic discovery: models are pulled by name (e.g. "x/z-image-turbo"); none pre-registered.
MODELS: list[Model] = []
