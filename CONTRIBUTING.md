# Contributing to Celeste AI

Thank you for your interest in contributing to Celeste AI! We welcome contributions from the community and are excited to have you on board.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
  - [Making Changes](#making-changes)
  - [Code Style](#code-style)
  - [Type Checking](#type-checking)
  - [Testing](#testing)
  - [Security](#security)
- [Adding a New Provider](#adding-a-new-provider)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

Please be respectful and constructive in all interactions. We are committed to providing a welcoming and inclusive environment for everyone.

## Getting Started

### Prerequisites

- **Python 3.12+** - Celeste requires Python 3.12 or higher
- **[uv](https://docs.astral.sh/uv/)** - We use `uv` for dependency management
- **Git** - For version control

### Development Setup

1. **Fork and clone the repository:**

   ```bash
   git clone https://github.com/YOUR_USERNAME/celeste-python.git
   cd celeste-python
   ```

2. **Install dependencies:**

   ```bash
   make sync
   ```

   This will install all dependencies including development tools and all capability packages.

3. **Verify setup:**

   ```bash
   make ci
   ```

   This runs the full CI pipeline locally to ensure everything is working.

## Project Structure

Celeste uses a monorepo structure with workspaces:

```
celeste-python/
├── src/celeste/              # Core library
│   ├── client.py             # Base client interface
│   ├── models.py             # Core data models
│   ├── http.py               # HTTP utilities
│   ├── streaming.py          # Streaming support
│   └── ...
├── packages/
│   ├── capabilities/         # Capability packages
│   │   ├── text-generation/
│   │   ├── image-generation/
│   │   ├── video-generation/
│   │   └── speech-generation/
│   └── providers/            # Provider-specific packages
│       ├── openai/
│       ├── anthropic/
│       ├── google/
│       └── ...
├── tests/
│   └── unit_tests/           # Core library tests
├── Makefile                  # Development commands
└── pyproject.toml            # Project configuration
```

### Key Concepts

- **Capabilities**: Abstract interfaces for AI functionalities (text generation, image generation, etc.)
- **Providers**: Concrete implementations for specific AI services (OpenAI, Anthropic, Google, etc.)
- **Core Library**: Shared utilities, base classes, and type definitions

## Development Workflow

### Making Changes

1. **Create a feature branch:**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style guidelines below.

3. **Run the CI pipeline locally:**

   ```bash
   make ci
   ```

4. **Commit your changes** with clear, descriptive commit messages.

### Code Style

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting.

- **Run linting:**

  ```bash
  make lint
  ```

- **Auto-fix linting issues:**

  ```bash
  make lint-fix
  ```

- **Format code:**

  ```bash
  make format
  ```

#### Style Guidelines

- Use type hints for all function parameters and return values
- Write docstrings for all public classes and functions
- Follow PEP 8 naming conventions
- Keep functions focused and single-purpose
- Prefer composition over inheritance where appropriate

### Type Checking

We use [mypy](https://mypy.readthedocs.io/) for static type checking. All code must pass type checking.

```bash
make typecheck
```

### Testing

We use [pytest](https://pytest.org/) for testing. Tests are organized into:

- **Unit tests**: Fast, isolated tests in `tests/unit_tests/` and `packages/*/tests/unit_tests/`
- **Integration tests**: Tests requiring API keys in `packages/*/tests/integration_tests/`

#### Running Tests

- **Run unit tests with coverage:**

  ```bash
  make test
  ```

  Unit tests must maintain **80% code coverage**.

- **Run integration tests (requires API keys):**

  ```bash
  make integration-test
  ```

- **Run integration tests for a specific capability:**

  ```bash
  make integration-test image-generation
  ```

#### Writing Tests

- Place unit tests in the appropriate `unit_tests/` directory
- Use `pytest.mark.integration` for integration tests
- Use `pytest.mark.slow` for slow-running tests
- Mock external API calls in unit tests
- Use `pytest-asyncio` for async test functions

### Security

We use [Bandit](https://bandit.readthedocs.io/) for security scanning.

```bash
make security
```

## Adding a New Provider

To add support for a new AI provider:

### 1. Create Provider Package (if needed)

If the provider doesn't exist yet, create a new package in `packages/providers/`:

```
packages/providers/your-provider/
├── pyproject.toml
└── src/
    └── celeste_your_provider/
        ├── __init__.py
        └── py.typed
```

### 2. Implement Capability Support

Add the provider implementation to the relevant capability package(s). For example, to add text generation support:

1. Create the provider directory:

   ```
   packages/capabilities/text-generation/src/celeste_text_generation/providers/your_provider/
   ├── __init__.py
   ├── client.py
   ├── parameters.py
   └── streaming.py
   ```

2. Implement the client by extending the appropriate base class:

   ```python
   from celeste_text_generation.client import TextGenerationClient
   
   class YourProviderTextGenerationClient(TextGenerationClient):
       """Your provider client for text generation."""
       
       @classmethod
       def parameter_mappers(cls) -> list[ParameterMapper]:
           # Define parameter mappings
           ...
       
       def _init_request(self, inputs: TextGenerationInput) -> dict[str, Any]:
           # Initialize API request
           ...
       
       def _parse_content(self, response_data: dict[str, Any], **parameters) -> StructuredOutput:
           # Parse API response
           ...
   ```

3. Register the provider in the capability's `providers/__init__.py`:

   ```python
   from celeste_text_generation.providers.your_provider.client import (
       YourProviderTextGenerationClient,
   )
   
   # Add to PROVIDERS list
   (Provider.YOUR_PROVIDER, YourProviderTextGenerationClient),
   ```

### 3. Add Models

Register the provider's models in the appropriate models file so they can be resolved.

### 4. Write Tests

- Add unit tests for the client implementation
- Add integration tests (marked with `@pytest.mark.integration`)

### 5. Update Documentation

- Update the README if adding a major new provider
- Add any provider-specific configuration notes

## Pull Request Process

1. **Ensure all checks pass:**

   ```bash
   make ci
   ```

2. **Update documentation** if you've changed APIs or added features.

3. **Write clear PR description:**
   - What problem does this solve?
   - How does it solve the problem?
   - Any breaking changes?

4. **Request review** from maintainers.

5. **Address feedback** promptly and thoroughly.

### PR Requirements

- All CI checks must pass
- Unit test coverage must not decrease
- Type hints must be complete
- Code must be formatted with Ruff
- No security issues flagged by Bandit

## Reporting Issues

### Bug Reports

Please include:
- Python version
- Celeste version
- Provider being used
- Minimal reproduction steps
- Expected vs actual behavior
- Error messages/stack traces

### Feature Requests

Please include:
- Use case description
- Proposed API/interface (if applicable)
- Any alternatives considered

---

## Questions?

- **GitHub Issues**: [celeste-python/issues](https://github.com/withceleste/celeste-python/issues)
- **Documentation**: [withceleste.ai/docs](https://withceleste.ai/docs)

Thank you for contributing to Celeste AI! 🎉
