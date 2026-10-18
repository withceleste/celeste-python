# Templates

Start from a template or, for an existing protocol, an existing compatible provider (route 2). When copying a template, replace the `{placeholders}` and strip the `.template` extension. Never write provider or modality files from scratch.

## Which route

1. **New provider with its own wire API** — copy `providers/{provider_slug}/{api_slug}/` (wire mixin: HTTP + parsing, mappers with no `.name`) and `modalities/{modality_slug}/providers/{provider_slug}/` (composite client, `.name`-bound mappers, model catalog). Checklist: CONTRIBUTING.md "Adding a provider".
2. **Provider speaks an existing protocol** (`chatcompletions`, `openresponses`) — copy/adapt an existing compatible provider and reuse the clients, streams, and named mappers under `src/celeste/modalities/text/protocols/`. Thin adapters can subclass the text protocol client directly (Meta, Ollama, OpenRouter). For provider-specific wire behavior, adapt a protocol-derived wire mixin plus its modality client (for example, HuggingFace or Groq). Complete the provider auth and modality registration steps in CONTRIBUTING.md. `templates/protocols/` is for a new wire format (route 5).
3. **Second wire API on an existing provider** — copy only `providers/{provider_slug}/{api_slug}/` (including `__init__.py`). On the modality side: demote the existing `client.py` to `{old_api}.py` (classes renamed `{Provider}{Api}{Modality}Client`), give every mapper set in `parameters.py` its backend token (see Naming), add `{new_api}.py` with the same shape, and make `client.py` the dispatcher from `modalities/{modality_slug}/providers/{provider_slug}/_dispatcher.py.template`. Enum, auth, exports, and the `PROVIDERS` registry entry stay untouched. Checklist: CONTRIBUTING.md "Adding a second API to an existing provider".
4. **New modality** — copy `modalities/{modality_slug}/`, then register: the `Modality`, `Domain`, and `Operation` members and the `DOMAIN_OPERATION_TO_MODALITY` row in `src/celeste/core.py`; `_CLIENT_MAP`, the model loop, and `__all__` in `src/celeste/__init__.py`; `src/celeste/modalities/__init__.py`; the domain namespace in `src/celeste/namespaces/domains.py` and `src/celeste/namespaces/__init__.py`. New members, rows, and entries go last; import lists and `__all__` stay sorted. Checklist: CONTRIBUTING.md "Adding a modality".
5. **New wire protocol** — copy `protocols/{protocol_slug}/` into `src/celeste/protocols/<protocol>/`. Add a modality-specific protocol client, stream, and named mappers, using `src/celeste/modalities/text/protocols/` as the existing pattern. To expose `create_client(protocol=...)`, add the `Protocol` enum member and its modality entry in `_CLIENT_MAP`.

## Naming

| Thing | Name | Example |
|---|---|---|
| Wire mixin (`providers/`) | `{Provider}{Api}Client` | `GoogleInteractionsClient` |
| Registered modality client | `{Provider}{Modality}Client` | `GoogleTextClient` |
| Per-backend modality client | `{Provider}{Api}{Modality}Client` | `GoogleInteractionsTextClient` |
| Wire-mixin import (composition side) | `{Provider}{Api}Client as {Provider}{Api}Mixin` — always, collision or not | `CohereChatClient as CohereChatMixin` |
| Wire-stream import (composition side) | `{Provider}{Api}Stream as _{Provider}{Api}Stream` — always | `CohereChatStream as _CohereChatStream` |
| Wire config import | plain `from celeste.providers.{provider}.{api} import config` — never aliased | — |
| Mapper set, single-backend file | bare classes + one `{PROVIDER}_PARAMETER_MAPPERS` | `TemperatureMapper`, `COHERE_PARAMETER_MAPPERS` |
| Mapper set, multi-backend file | every set tokened: `{Backend}NameMapper` classes, `_{Backend}NameMapper` wire aliases, `{PROVIDER}_{BACKEND}_PARAMETER_MAPPERS` lists — no bare set survives | `VertexTemperatureMapper`, `GOOGLE_VERTEX_PARAMETER_MAPPERS` |
| Module functions, multi-backend file | backend-token suffix on every function | `map_grounding_vertex`, `map_grounding_interactions` |
| Public module-level data constants | `{PROVIDER}_...`; `MODELS` is the sole bare contract name | `GOOGLE_VOICES`, `GOOGLE_SUPPORTED_MIME_TYPES` |

The prefix is always the `Provider` enum name, never a brand or model family (`Google`, not `Gemini`). A family token may follow the provider prefix only when parallel same-kind constants partition the data (`GOOGLE_VEO_MODELS` / `GOOGLE_OMNI_MODELS`). The backend token is the backend file name (`veo.py` → `Veo`, `vertex.py` → `Vertex`, `interactions.py` → `Interactions`). Wire helper functions, protocol base clients, and module-private names (`_VEO_MODEL_IDS`) keep their real names.

## Notes

- The commented Vertex block in `providers/{provider_slug}/{api_slug}/client.py.template` is only for providers that serve the SAME wire API on both api-key and ADC auth (different host). A different wire format per auth is route 3, not a `_build_url` branch.
- When a modality stream needs events the base `_parse_chunk` filtering drops (tool calls, thought signatures), retain them: seed a private list in `__init__`, append in `_parse_chunk` before calling `super()`, and return it from the matching `_aggregate_*` hook (see the anthropic and google streams).
