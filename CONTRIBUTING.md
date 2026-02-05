# Contributing to Celeste

## TL;DR

- **Open an issue first** for non-trivial changes.
- Base PRs on `main`.
- Run `make ci` before pushing.
- **Template-first**: new providers/modalities must start by copying from `templates/`.

## Setup

**Prerequisites:** Python 3.12+, [uv](https://docs.astral.sh/uv/)

```bash
uv sync --group dev
uv run pre-commit install
uv run pre-commit install --hook-type pre-push
```

> Pre-commit runs linting, formatting, type checking, and security scans.
> Pre-push additionally runs the full unit test suite with coverage.

## Local checks

```bash
make ci          # Full pipeline: format, lint, typecheck, security, tests
make test        # Unit tests only
make lint        # Ruff linting
make format      # Ruff formatting
make typecheck   # mypy
make security    # Bandit scan
```

**Integration tests** hit real provider APIs (costs money, requires keys):

```bash
cp .env.example .env   # Fill in your API keys
make integration-test
```

## Before you start

Small fixes (typos, tests, minor bugfixes) — go ahead and open a PR directly.

For new providers, new modalities, new parameters, new models, constraint updates, or dependency additions — **open an issue first**.

Changes to parsing, streaming, or typing semantics **require explicit maintainer approval** before any work begins. These are core primitives that affect every provider and modality.

## Adding a provider

Always start by copying from the templates. Replace `{provider_slug}`, `{api_slug}` placeholders and strip the `.template` extension.

**Provider API layer** — copy from `templates/providers/`, place in `src/celeste/providers/<provider>/`:

1. Add the provider to the `Provider` enum in `src/celeste/core.py` (if new).
2. Register auth via `register_auth()` in `src/celeste/providers/<provider>/__init__.py`.
3. Export the provider in `src/celeste/providers/__init__.py`.
4. Fill in the scaffolded files: `config.py` (endpoints), `client.py` (HTTP + parsing), `parameters.py` (mappers), `streaming.py` (SSE).
5. The template contract is enforced by `tests/unit_tests/test_provider_api_templates.py` — `make test` will catch missing or mismatched methods.

**Modality wiring** — copy from `templates/modalities/`, place in `src/celeste/modalities/<modality>/providers/<provider>/`:

6. Define models in `models.py` (model IDs, operations, parameter constraints).
7. Create parameter mappers in `parameters.py` (inherit from provider API mappers, set modality-specific `name`).
8. Create the modality client + stream class in `client.py`.
9. Register models in `src/celeste/modalities/<modality>/models.py`.
10. Register the client in the `PROVIDERS` dict in `src/celeste/modalities/<modality>/providers/__init__.py`.
11. Add the provider's official API docs link to `src/celeste/providers/api_references.md`.

## Pull requests

Include:
- A short summary (what and why).
- A test plan (`make ci` output, plus any integration tests you ran).
- If you touched provider behavior: provider, model ID, and endpoints tested.

## Issues

- **Bug reports**: Celeste version, Python version, provider/model/operation, minimal repro, expected vs actual.
- **Provider requests**: official API docs link, auth method, required endpoints, streaming format, usage/finish semantics.

## Security

Do not open public issues for vulnerabilities. Email `kamil@withceleste.ai` or use GitHub's private vulnerability reporting.

## Community

Be kind, constructive, and respectful. Contact `kamil@withceleste.ai` for any concerns.

## License

By contributing, you agree your contributions are licensed under the MIT license (see [LICENSE](LICENSE)).
