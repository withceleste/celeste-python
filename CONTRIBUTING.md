# Contributing to Celeste AI

Thank you for your interest in contributing to Celeste AI! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
  - [Branching Strategy](#branching-strategy)
  - [Making Changes](#making-changes)
  - [Code Style](#code-style)
  - [Type Annotations](#type-annotations)
- [Testing](#testing)
  - [Running Tests](#running-tests)
  - [Writing Tests](#writing-tests)
  - [Test Markers](#test-markers)
- [Pre-commit Hooks](#pre-commit-hooks)
- [Submitting Changes](#submitting-changes)
  - [Commit Message Format](#commit-message-format)
  - [Pull Request Process](#pull-request-process)
- [Adding a New Provider](#adding-a-new-provider)
- [Project Architecture](#project-architecture)
- [Getting Help](#getting-help)

---

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and constructive in all interactions.

---

## Getting Started

### Prerequisites

- **Python 3.12+** - The project requires Python 3.12 or later
- **[uv](https://docs.astral.sh/uv/)** - Fast Python package manager (recommended)
- **Git** - Version control

### Development Setup

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/YOUR_USERNAME/celeste-python.git
   cd celeste-python
   ```

2. **Install dependencies with uv**

   ```bash
   # Install uv if you haven't already
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Sync all dependencies including dev tools
   make sync
   # or manually:
   uv sync --all-packages --all-extras
   ```

3. **Install pre-commit hooks**

   ```bash
   uv run pre-commit install
   uv run pre-commit install --hook-type pre-push
   ```

4. **Verify your setup**

   ```bash
   make ci
   ```

---

## Development Workflow

### Branching Strategy

- `main` - Production-ready code, protected branch
- `develop` - Integration branch for features (if used)
- Feature branches - Create from `main` with descriptive names

**Branch naming conventions:**

```
feat/add-new-provider
fix/handle-timeout-error
docs/update-readme
refactor/simplify-client
```

### Making Changes

1. Create a new branch from `main`:

   ```bash
   git checkout main
   git pull origin main
   git checkout -b feat/your-feature-name
   ```

2. Make your changes following the code style guidelines

3. Run the full CI pipeline locally before committing:

   ```bash
   make ci
   ```

4. Commit your changes using conventional commits (see below)

5. Push and create a pull request

### Code Style

We use **Ruff** for both linting and formatting. The configuration is in `pyproject.toml`.

```bash
# Check for linting issues
make lint

# Auto-fix linting issues
make lint-fix

# Format code
make format
```

**Key style guidelines:**

- Line length: 88 characters (Black-compatible)
- Use double quotes for strings
- Sort imports with isort (handled by Ruff)
- Follow PEP 8 naming conventions

### Type Annotations

We enforce **strict type checking** with MyPy. All code must have complete type annotations.

```bash
make typecheck
```

**Type annotation requirements:**

- All function parameters must have type hints
- All function return types must be specified
- Use `typing` module types where appropriate
- Generic types should use proper type parameters

**Example:**

```python
from typing import TypeVar

T = TypeVar("T")

def process_items(items: list[T], callback: Callable[[T], None]) -> int:
    """Process items and return count."""
    for item in items:
        callback(item)
    return len(items)
```

---

## Testing

### Running Tests

```bash
# Run unit tests with coverage (80% minimum required)
make test

# Run specific test file
uv run pytest tests/unit_tests/test_models.py -v

# Run tests matching a pattern
uv run pytest tests/unit_tests -k "test_name" -v

# Run integration tests (requires API keys)
make integration-test

# Run tests in parallel
uv run pytest tests/unit_tests -n auto
```

### Writing Tests

We follow these testing principles:

- **AAA Pattern**: Arrange, Act, Assert
- **Descriptive names**: `test_user_cannot_login_with_invalid_password`
- **One assertion per test** (testing one behavior)
- **Use fixtures** over setup/teardown
- **Isolate tests**: Use the `clear_registry` fixture for model registry isolation

**Test file structure:**

```
tests/
├── unit_tests/          # Fast tests, no API calls
│   ├── conftest.py      # Shared fixtures
│   ├── test_models.py
│   └── test_client.py
└── integration_tests/   # Require API keys
    └── test_openai.py
```

**Example test:**

```python
import pytest
from celeste.models import register_models, get_model

@pytest.mark.smoke
def test_get_model_returns_registered_model(clear_registry):
    """Test that get_model returns a previously registered model."""
    # Arrange
    register_models([model_fixture])

    # Act
    result = get_model("test-model")

    # Assert
    assert result.id == "test-model"
```

### Test Markers

Use markers to categorize tests:

```python
@pytest.mark.smoke        # Critical path tests, run frequently
@pytest.mark.slow         # Long-running tests
@pytest.mark.integration  # Requires API keys/external services
```

Run specific markers:

```bash
uv run pytest -m smoke           # Only smoke tests
uv run pytest -m "not slow"      # Exclude slow tests
uv run pytest -m integration     # Only integration tests
```

---

## Pre-commit Hooks

Pre-commit hooks run automatically on commit. They include:

| Hook | Description |
|------|-------------|
| `trailing-whitespace` | Remove trailing whitespace |
| `end-of-file-fixer` | Ensure files end with newline |
| `check-yaml` | Validate YAML syntax |
| `check-toml` | Validate TOML syntax |
| `check-json` | Validate JSON syntax |
| `check-merge-conflict` | Prevent committing merge conflicts |
| `debug-statements` | Prevent committing print()/pdb statements |
| `no-commit-to-branch` | Prevent direct commits to main/master/develop |
| `ruff-check` | Lint with Ruff |
| `ruff-format` | Format with Ruff |
| `mypy` | Type checking |
| `bandit` | Security scanning |

**On push** (not commit):

| Hook | Description |
|------|-------------|
| `pytest` | Run unit tests with coverage |

To run hooks manually:

```bash
uv run pre-commit run --all-files
```

---

## Submitting Changes

### Commit Message Format

We use **Conventional Commits**. Format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Code style (formatting, no logic change) |
| `refactor` | Code refactoring (no feature/fix) |
| `perf` | Performance improvement |
| `test` | Adding/updating tests |
| `chore` | Maintenance tasks |
| `ci` | CI/CD changes |

**Examples:**

```bash
feat(text): add streaming support for Anthropic provider
fix(images): handle timeout errors in DALL-E client
docs: update installation instructions
test(audio): add unit tests for transcription
refactor(client): simplify parameter validation logic
```

### Pull Request Process

1. **Ensure all checks pass locally:**

   ```bash
   make ci
   ```

2. **Push your branch and create a PR:**

   ```bash
   git push origin feat/your-feature-name
   ```

3. **Fill out the PR template:**
   - Clear description of changes
   - Link to related issues
   - Screenshots/examples if applicable

4. **PR requirements:**
   - All CI checks must pass
   - Code coverage must remain at or above 80%
   - At least one approval required
   - No merge conflicts

5. **After review:**
   - Address feedback with new commits
   - Squash commits if requested
   - Maintainer will merge when ready

---

## Adding a New Provider

To add support for a new AI provider:

1. **Create provider directory structure:**

   ```
   src/celeste/providers/{provider_name}/
   ├── __init__.py
   └── {modality}/           # e.g., text/, images/
       ├── __init__.py
       ├── client.py         # Provider-specific client
       ├── parameters.py     # Parameter mappings
       └── models.py         # Model definitions
   ```

2. **Implement the client:**

   ```python
   # providers/{provider}/text/client.py
   from celeste.modalities.text.client import TextClient

   class ProviderTextClient(ProviderMixin, TextClient):
       async def generate(self, inputs: TextInput, **parameters):
           request = self._build_request(inputs, parameters)
           response = await self._make_request(request)
           return self._parse_response(response)
   ```

3. **Register models in `models.py`:**

   ```python
   from celeste.models import Model, register_models

   PROVIDER_MODELS = [
       Model(
           id="model-name",
           provider=Provider.YOUR_PROVIDER,
           # ... model configuration
       ),
   ]

   register_models(PROVIDER_MODELS)
   ```

4. **Add the provider to `core.py`:**

   ```python
   class Provider(str, Enum):
       # ... existing providers
       YOUR_PROVIDER = "your_provider"
   ```

5. **Write tests:**
   - Unit tests in `tests/unit_tests/`
   - Integration tests in `tests/integration_tests/` (marked with `@pytest.mark.integration`)

6. **Update documentation** if needed

---

## Project Architecture

```
src/celeste/
├── core.py           # Enums: Provider, Modality, Operation
├── models.py         # Model registry
├── client.py         # Base ModalityClient and APIMixin
├── constraints.py    # Parameter validation
├── parameters.py     # Parameter mapping system
├── modalities/       # By-modality organization
│   ├── text/
│   ├── images/
│   ├── audio/
│   ├── videos/
│   └── embeddings/
├── providers/        # By-provider implementations
│   └── {provider}/{modality}/
└── namespaces/       # High-level API entry points
```

**Key concepts:**

- **Modality-first design**: Organized by what you produce (text, images, etc.)
- **Provider multiplexing**: Same interface, multiple providers
- **Async-first**: All implementations are `async def`, sync via `asgiref`
- **Type-safe**: Full Pydantic validation and strict MyPy

For detailed architecture documentation, see [AGENTS.md](AGENTS.md).

---

## Getting Help

- **Questions**: Open a [GitHub Discussion](https://github.com/withceleste/celeste-python/discussions)
- **Bug reports**: Open a [GitHub Issue](https://github.com/withceleste/celeste-python/issues)
- **Feature requests**: Open a [GitHub Issue](https://github.com/withceleste/celeste-python/issues/new)
- **Security issues**: Email security@withceleste.ai (do not open public issues)

---

## Recognition

Contributors are recognized in our release notes. Thank you for helping make Celeste AI better!
