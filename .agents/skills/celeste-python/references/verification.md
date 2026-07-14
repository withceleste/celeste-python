# Celeste Verification Reference

Use focused tests first, then broader commands when the blast radius warrants it.

## Commands

Focused unit test:

```bash
uv run pytest tests/unit_tests/<file>.py -q
```

Read-only or failure-only repo checks:

```bash
make lint
make typecheck
make test
```

Mutation-intended finalization commands:

```bash
make format
make ci
```

`make format` rewrites files. Current `make ci` runs `lint-fix` and `format`, so treat it as mutating.

Integration tests require provider credentials and are not default for local verification.

## Test Matrix By Seam

Public exports, client factory, model resolution:

```bash
uv run pytest tests/unit_tests/test_init.py -q
```

Model registry and filtering:

```bash
uv run pytest tests/unit_tests/test_models.py -q
```

ModalityClient request building, output construction, metadata, warnings, streaming:

```bash
uv run pytest tests/unit_tests/test_client.py -q
```

Parameter `TypedDict`s and `ParameterMapper` behavior:

```bash
uv run pytest tests/unit_tests/test_parameters.py tests/unit_tests/test_parameter_wire_contracts.py -q
```

Constraints and optional input support:

```bash
uv run pytest tests/unit_tests/test_constraints.py tests/unit_tests/test_io.py -q
```

Protocol and base URL routing:

```bash
uv run pytest tests/unit_tests/test_protocol_base_url.py -q
```

Vertex/provider auth routing:

```bash
uv run pytest tests/unit_tests/test_vertex_routing.py -q
```

Structured outputs:

```bash
uv run pytest tests/unit_tests/test_structured_outputs.py -q
```

Tools, tool choice, tool outputs, and tool-call validation:

```bash
uv run pytest tests/unit_tests/test_tool_choice.py tests/unit_tests/test_tool_outputs.py tests/unit_tests/test_text_tool_results.py tests/unit_tests/test_google_tools_mapper.py tests/unit_tests/test_tool_call_validation.py -q
```

Artifacts and MIME types:

```bash
uv run pytest tests/unit_tests/test_artifacts.py -q
```

Multimodal text messages and media support validation:

```bash
uv run pytest tests/unit_tests/test_text_multimodal_message_content.py tests/unit_tests/test_text_multimodal_message_request_building.py tests/unit_tests/test_text_media_support_validation.py -q
```

Document analysis convenience path:

```bash
uv run pytest tests/unit_tests/test_text_modality_analyze_document.py -q
```

Embeddings input and multimodal embeddings:

```bash
uv run pytest tests/unit_tests/test_embeddings_input.py tests/unit_tests/test_embeddings_multimodal.py -q
```

Streaming metadata:

```bash
uv run pytest tests/unit_tests/test_streaming.py tests/unit_tests/test_stream_metadata_from_response_data.py -q
```

Telemetry content and streaming:

```bash
uv run pytest tests/unit_tests/test_telemetry_content_events.py tests/unit_tests/test_telemetry_streaming.py tests/unit_tests/test_telemetry_metrics.py -q
```

## When To Run Broader Checks

Run `make test` when a change touches shared client behavior, model registry, constraints, parameters, artifacts, tools, or multiple providers.

Run `make typecheck` when changing signatures, `TypedDict`s, generic client classes, or public exports.

Run mutation-intended finalization commands only when file rewrites are acceptable.

If a command cannot run because dependencies or credentials are missing, state that explicitly and describe the remaining risk.
