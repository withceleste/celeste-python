# CLAUDE.md

This file provides guidance to Agents when working with code in this repository.

## Project Overview

Celeste AI is a type-safe, provider-agnostic SDK for multi-modal AI. It provides a unified interface to 15+ AI providers (OpenAI, Anthropic, Google, Mistral, Ollama, etc.) across multiple modalities (Text, Images, Audio, Video, Embeddings).

**Philosophy:** "Primitives, not frameworks" - clean I/O without lock-in.

## Commands

```bash
# Dependencies (uses uv package manager)
make sync              # Update and sync all dependencies

# Quality checks
make lint              # Ruff linting check
make lint-fix          # Ruff auto-fix
make format            # Ruff formatting
make typecheck         # MyPy type checking
make security          # Bandit security scan
make ci                # Full CI pipeline (lint, format, typecheck, security, test)

# Testing
make test              # Unit tests with coverage (80% minimum)
make integration-test  # Integration tests (requires API keys)

# Run specific tests
uv run pytest tests/unit_tests/test_models.py -v
uv run pytest tests/unit_tests -k "test_name" -v
```

## Architecture

### Core Design: Modality-First with Provider Multiplexing

The SDK is organized around **what you produce** (modality) and **where it comes from** (provider):

```
src/celeste/
├── core.py           # Enums: Provider, Modality, Operation
├── models.py         # Model registry: register_models(), get_model(), list_models()
├── client.py         # Base ModalityClient and APIMixin
├── constraints.py    # Parameter validation (Range, Choice, Pattern, etc.)
├── parameters.py     # Parameter mapping system
├── modalities/       # By-modality organization
│   ├── text/         # client.py, io.py, parameters.py, streaming.py, models.py
│   ├── images/
│   ├── audio/
│   ├── videos/
│   └── embeddings/
├── providers/        # By-provider implementations (19 providers)
│   └── {provider}/{modality}/  # Each has client.py, parameters.py, models.py
└── namespaces/       # High-level API: celeste.text, celeste.images, etc.
```

### Key Abstractions

1. **Model Registry** (`models.py`): Central registry mapping `(model_id, provider)` to `Model` objects with capabilities, operations, and parameter constraints.

2. **ModalityClient** (`client.py`): Generic base class `ModalityClient[Input, Output, Parameters, Content]` handling sync/async delegation.

3. **Parameter System** (`parameters.py`, `constraints.py`):
   - `ParameterMapper`: Transforms provider-specific parameters to unified format
   - `Constraint`: Validates parameters (Range, Choice, Pattern, Min, Max)

4. **Domain Namespaces** (`namespaces/domains.py`): Entry points supporting:
   - Async: `celeste.text.generate()`
   - Sync: `celeste.text.sync.generate()`
   - Streaming: `celeste.text.stream.generate()`

### Provider Implementation Pattern

```python
# In providers/{provider}/{modality}/client.py:
class ProviderTextClient(ProviderMixin, TextClient):
    async def generate(self, inputs: TextInput, **parameters):
        request = self._build_request(inputs, parameters)
        response = await self._make_request(request)
        return self._parse_response(response)
```

## Key Conventions

- **Async-first**: Implementations use `async def`, sync versions via `asgiref.sync.async_to_sync()`
- **Type hints everywhere**: Strict MyPy enforced (`disallow_untyped_defs=true`)
- **Pydantic v2**: Full validation with IDE autocomplete
- **Test isolation**: Use `clear_registry` fixture to isolate model registry between tests
- **Conventional Commits**: `feat(scope):`, `fix:`, `test:`, `docs:`, `refactor:`

## Public API

```python
from celeste import create_client, Modality, Operation, Provider

# High-level API (preferred)
text = await celeste.text.generate("prompt", model="claude-opus-4-5")
image = await celeste.images.generate("prompt", model="flux-2-pro")

# Explicit client creation
client = create_client(
    modality=Modality.TEXT,
    operation=Operation.GENERATE,
    provider=Provider.ANTHROPIC,
    model="claude-opus-4-5",
)
```

## Testing Notes

- Unit tests: `tests/unit_tests/` - fast, no API calls, 80% coverage minimum
- Integration tests: `tests/integration_tests/` - require API keys, marked with `@pytest.mark.integration`
- Use `@pytest.mark.smoke` for critical path tests
- Use `@pytest.mark.parametrize` for multiple input combinations
- Tests use `pytest-asyncio` with `asyncio_mode = "auto"`
