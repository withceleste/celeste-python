"""Ollama models for images modality.

Ollama uses dynamic model discovery - models are pulled by name.
Users specify model IDs like 'x/z-image-turbo' or 'gemma3:4b'.
No pre-registered models needed.
"""

from celeste.models import Model

MODELS: list[Model] = []
