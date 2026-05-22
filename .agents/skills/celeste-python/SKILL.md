---
name: celeste-python
description: Use whenever writing, modifying, reviewing, or debugging code involving Celeste, celeste-ai, celeste-python, import celeste, src/celeste, or withceleste app integrations. This includes providers, modalities, models, artifacts, MIME types, parameters, tools, multimodal messages, streaming, structured outputs, protocol/base URL support, OpenSpec changes, and tests. Always use this skill before inventing Celeste types, registries, model catalogs, provider abstractions, request/response shapes, or syntax.
compatibility: Local celeste-python repository skill; no network required.
---

# Celeste Python Coding

Use this skill to stay aligned with the actual Celeste SDK in this repository.
Celeste is evolving, so current source and tests are more reliable than model memory.

## First Step

Read `references/repo-map.md` before making Celeste-related code changes or review claims.
It gives the current public API, internal layering, extension seams, templates, and canonical tests.

Then read only the references relevant to the task:

- App-side integration: `references/public-api.md`
- SDK-internal provider, modality, model, parameter, protocol, streaming, or tool work: `references/sdk-architecture.md`
- Review/debugging or suspicious Celeste code: `references/anti-patterns.md`
- Test selection or final checks: `references/verification.md`

## Source-Of-Truth Order

When sources disagree, follow this order:

1. Current source code in `src/celeste/`
2. Current tests and templates for existing behavior
3. README examples and public exports
4. Active OpenSpec artifacts for intended new behavior and acceptance criteria
5. Notes such as `common_agent_mistakes.md`
6. Model memory

Treat `common_agent_mistakes.md` as advisory. Verify every warning against current code and the task context.

## Route The Task

Classify the task before coding:

- App integration: code outside the SDK consuming Celeste. Prefer public namespaces and public exports. Keep the boundary thin.
- SDK internals: changes inside `src/celeste`, `templates`, or tests. Follow existing modality, provider, protocol, model, mapper, and streaming patterns.
- Review/debugging: identify whether issues are app-side duplication, SDK pattern drift, unsupported model/parameter assumptions, or test gaps.

## App Integration Rules

Use the public API first:

- `celeste.text.*`
- `celeste.images.*`
- `celeste.audio.*`
- `celeste.videos.*`
- `celeste.documents.*`

Use `create_client(...)` when explicit client reuse or explicit `modality`, `operation`, `provider`, `protocol`, `base_url`, or auth configuration is needed.

Do not create app-local duplicates for Celeste-owned concepts unless the user explicitly asks for a temporary compatibility layer. Import and use Celeste types for roles, providers, modalities, operations, artifacts, MIME types, tools, and model discovery.

## SDK Internal Rules

Do not flatten Celeste into a single invented abstraction. The SDK intentionally separates:

- provider auth registration
- modality provider maps
- provider API mixins
- modality-specific provider clients
- per-modality model aggregation
- parameter enums and `ParameterMapper`s
- constraints and optional input type inference
- protocol clients for compatible APIs

Start from nearby existing providers/modalities and templates. Use focused tests as executable documentation.

## Common Failure Modes

Before adding new local code, check whether Celeste already owns the concept.
Watch for:

- raw provider, role, MIME, modality, operation, or input-type strings where Celeste exposes enums
- app-side model allowlists where `list_models(...)` or the host app's existing Celeste discovery flow should be used
- runtime registry patching from app code
- provider SDK request shapes copied directly into app code
- new parameter names without modality enums, `TypedDict` fields, model constraints, and provider mappers
- provider registration changes that update one seam but miss auth, modality maps, model aggregation, or tests

## Verification

Pick focused tests from `references/verification.md` based on the seam touched.
For broader read-only checks, use the repo commands:

- `make lint`
- `make typecheck`
- `make test`

For finalization commands that may rewrite files, use them only when mutation is intended:

- `make format`
- `make ci` (runs lint-fix and format internally)

If you cannot run a relevant command, say so and explain the remaining risk.
