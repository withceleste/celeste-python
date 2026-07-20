# Contributing to Celeste

## TL;DR

- **Open an issue first** for non-trivial changes.
- Base PRs on `main`.
- Run `make ci` before pushing.
- **Template-first**: new providers/modalities must start by copying from `templates/`.

## Setup

**Prerequisites:** Python 3.12+, [uv](https://docs.astral.sh/uv/)

```bash
uv sync --all-extras
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

Vertex-path tests authenticate via ADC, not `.env` keys: `gcloud auth application-default login` with an account that has `roles/aiplatform.user` on the project and a usable quota project. Claude-on-Vertex additionally needs the model enabled in the project's Model Garden.

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
5. Run `make typecheck` and the relevant provider integration tests.

**Modality wiring** — copy from `templates/modalities/`, place in `src/celeste/modalities/<modality>/providers/<provider>/`:

6. Define models in `models.py` (model IDs, operations, parameter constraints).
7. Create parameter mappers in `parameters.py` (inherit from provider API mappers, set modality-specific `name`).
8. Create the modality client + stream class in `client.py`.
9. Register models in `src/celeste/modalities/<modality>/models.py`.
10. Register the client in the `PROVIDERS` dict in `src/celeste/modalities/<modality>/providers/__init__.py`.
11. Add the provider's official API docs link to `src/celeste/providers/api_references.md`.

### Protocol-based providers

A protocol is a wire format served by many vendors (`chatcompletions`, `openresponses`). Vendors that speak one (DeepSeek, Moonshot, Groq, Mistral, HuggingFace, ...) subclass the shared protocol client from `src/celeste/protocols/` instead of copying the full provider template — templates live at `templates/protocols/`. Editing a protocol changes every inheriting vendor: vendor-specific behavior goes in that vendor's own `client.py` / `parameters.py` override, never in the shared base.

### Adding a second API to an existing provider

The steps above assume a new provider. For a new wire API on an existing one (e.g. Interactions next to GenerateContent), the delta is:

1. Steps 1–3 are already done — enum, auth, and exports stay untouched.
2. Copy `templates/providers/` into `src/celeste/providers/<provider>/<new_api>/`, including `__init__.py`.
3. On the modality side, rename the existing `client.py` to `<old_api>.py` and its classes `{Provider}{Modality}Client` → `{Provider}{Api}{Modality}Client`; the new backend lands in `<new_api>.py` with the same shape.
4. The new `client.py` is the dispatcher (`templates/modalities/{modality_slug}/providers/{provider_slug}/_dispatcher.py.template`): selects a backend in `model_post_init`, merges mapper lists, copies endpoint ClassVars, and forwards every hook a backend customizes — `tests/unit_tests/test_dispatcher_delegation.py` fails CI naming any hook you missed (`ModalityClient`'s docstring describes the hook surface).
5. `parameters.py` now serves two backends, so every set carries its backend token: rename the existing classes to `{Api1}NameMapper` and the existing list to `{PROVIDER}_{API1}_PARAMETER_MAPPERS`, then add the parallel `{Api2}` set with `{PROVIDER}_{API2}_PARAMETER_MAPPERS` — no bare set survives in a multi-backend file. Same-file helper functions take the backend token as a suffix (`map_grounding_vertex` / `map_grounding_interactions`).
6. Step 10 is a no-op: the `PROVIDERS` entry keeps pointing at `{Provider}{Modality}Client` — the registry never branches.
7. Live probes before pinning: the endpoint version must serve every catalog model (stable and preview ids); `Model.streaming` flips only after a live call through celeste's stream path; model ids verified against the new API's reference. A mapper may only write fields that exist in that reference — the wire-contract matrix asserts our mapping, not the API's truth.
8. Tests: dispatch-selection asserts on `client._strategy`, per-backend `_init_request` payload tests, and wire-contract matrix rows for the new mapper list. The delegation guard (`tests/unit_tests/test_dispatcher_delegation.py`) picks the new dispatcher up automatically from the registry — no new rows.
9. Before calling it done, run the provider's integration tests (`make integration-test`) — they are the only check that proves wire fields against the live API. Sort failures into billing / auth / pre-existing before treating any as a code defect; when the API reference and live serving disagree, live serving wins.

## Model catalog rules

- `Model.streaming` means celeste's adapter transport streams this model — not the vendor's advertised capability.
- A `MAX_TOKENS` Range comes only from a provider-documented max-completion/output figure; a context window is never a completion cap. No documented completion max → omit the constraint.
- Choice/enum literals verbatim from the provider's API request-parameter reference, not marketing pages. Conflicting official pages → keep the current value, record the conflict.
- One `parameter_constraints` dict serves every call mode (unary and streaming): constrain to the union, let the provider reject mode-specific invalids.
- Parameters with no constraint pass through unvalidated by design — do not add local guards for values the provider itself rejects.

See CLAUDE.md for the full rules.

## Removing a model

Remove a model id only after a live authenticated call hard-rejects it. Provider lifecycle/deprecation tables are announcements, not serving status — providers keep "retired" aliases serving or silently redirect them (e.g. `pixtral-12b-latest` serves `ministral-14b-latest`). Precedent: PRs #280, #311, #314.

## Testing

- `make ci` is the gate. Wire-contract tests are data-driven over mapper lists (`_map` / `_at` in `tests/unit_tests/test_parameter_wire_contracts.py`); request-payload tests call `client._init_request(...)` directly; stream parse tests instantiate via `object.__new__(...)`; never mock httpx in provider/parameter tests (only `tests/unit_tests/test_http.py` touches the transport).
- A test must earn its place: focused, guarding real behavior, parametrized over cases instead of duplicated. No test ceremony, no coverage bloat. If a test is not clearly required, no test is better than a weak one.

## Pull requests

Include:
- A short summary (what and why).
- A test plan (`make ci` output, plus any integration tests you ran).
- If you touched provider behavior: provider, model ID, and endpoints tested.

Address review feedback with follow-up commits — never amend or force-push a branch under review.

## Issues

- **Bug reports**: Celeste version, Python version, provider/model/operation, minimal repro, expected vs actual.
- **Provider requests**: official API docs link, auth method, required endpoints, streaming format, usage/finish semantics.

## Security

Do not open public issues for vulnerabilities. Email `kamil@withceleste.ai` or use GitHub's private vulnerability reporting.

## Community

Be kind, constructive, and respectful. Contact `kamil@withceleste.ai` for any concerns.

## License

By contributing, you agree your contributions are licensed under the MIT license (see [LICENSE](LICENSE)).
