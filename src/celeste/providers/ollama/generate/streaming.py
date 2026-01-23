"""Ollama Generate streaming (stub - NDJSON not supported in v1).

Ollama uses NDJSON streaming, not SSE. This would require different
parsing logic in celeste.http. For v1, streaming is not supported.
"""

__all__: list[str] = []
