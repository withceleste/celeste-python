# Celeste consistency review todo list

Use these stable numbers in commits and the ongoing pull request. Do not renumber completed items. Update each checkbox and the PR description as its change lands.

Progress: 1 of 48 items completed.

Items 36–46 include narrowly scoped findings and unresolved support-contract decisions; retain those qualifications when implementing them. All items are open until their fix or documented decision is verified.

## Templates and contribution guidance

- [x] **1. Fix circular catalog imports.** Import `Model` and `Provider` from their defining modules so a rendered catalog can load during `import celeste`. [Source](templates/modalities/{modality_slug}/providers/{provider_slug}/models.py.template). The [fresh-process regression](tests/unit_tests/test_catalog_template.py) failed before the import change and passes afterward, including discovery of the rendered model.
- [ ] **2. Align companion mapper names.** The composite template imports `ExampleMapper`, while the wire template defines `ExampleParamMapper`. [Source](templates/modalities/{modality_slug}/providers/{provider_slug}/parameters.py.template).
- [ ] **3. Add the required provider `_init_request` hook.** The generated provider client remains abstract after its explicit TODOs are implemented. [Source](templates/modalities/{modality_slug}/providers/{provider_slug}/client.py.template).
- [ ] **4. Bind the generated modality usage class.** Missing `_usage_class` causes generated output validation to reject base `Usage` objects. [Source](templates/modalities/{modality_slug}/client.py.template).
- [ ] **5. Bind the generated modality finish-reason class.** Missing `_finish_reason_class` fails when a provider returns the base wire `FinishReason`; the composite wrapper can mask this. [Source](templates/modalities/{modality_slug}/client.py.template).
- [ ] **6. Add async modality operation methods.** The template has sync/stream `generate` and `analyze`, but no async counterparts; correct the stated ownership of operation methods. [Source](templates/modalities/{modality_slug}/client.py.template).
- [ ] **7. Correct compatible-provider scaffolding guidance.** Distinguish creating a protocol from adding a vendor that subclasses an existing protocol; update CONTRIBUTING.md too. [Source](templates/README.md).
- [ ] **8. Honor `base_url` in the provider template.** Unary and streaming transports hardcode `config.BASE_URL`. [Source](templates/providers/{provider_slug}/{api_slug}/client.py.template).
- [ ] **9. Correct the structured-output example in the protocol template.** Do not unconditionally parse empty tool-only response content as JSON. [Source](templates/protocols/{protocol_slug}/parameters.py.template).
- [ ] **10. Handle nullable usage in the protocol template.** Explicit `usage: null` is currently passed to dictionary-based usage mapping. [Source](templates/protocols/{protocol_slug}/client.py.template).

## Shared protocol behavior

- [ ] **11. Preserve tool-only turns when an output schema is supplied.** OpenResponses, Chat Completions, Google Interactions, and GenerateContent call `json.loads("")` before returning tools. Cover unary and streaming paths. [Source](src/celeste/protocols/openresponses/parameters.py).
- [ ] **12. Repair references in list output schemas.** OpenResponses, Anthropic, and HuggingFace nest `$defs` while retaining root-relative references for lists of nested Pydantic models. [Source](src/celeste/protocols/openresponses/parameters.py).
- [ ] **13. Align response schema aliases with validation aliases.** OpenAI, Anthropic, HuggingFace, Cohere, and Mistral can request serialization aliases that their response validation rejects. Symmetric `Field(alias=...)` works. [Source](src/celeste/protocols/openresponses/parameters.py).
- [ ] **14. Map or reject forced native tool choices correctly.** OpenResponses and both Google implementations emit null function names or allowed-name entries for native tools. [Source](src/celeste/protocols/openresponses/parameters.py).
- [ ] **15. Preserve unary refusal responses.** OpenResponses returns empty completed content and removes the refusal from metadata; streaming retains the raw refusal. [Source](src/celeste/protocols/openresponses/tools.py).
- [ ] **16. Stop substituting empty arguments for malformed tool JSON.** Chat Completions unary/stream parsing replaces truncated arguments with `{}`, which defaulted schemas can accept. Preserve an error/incomplete state; the overall length finish reason currently remains available. [Source](src/celeste/protocols/chatcompletions/tools.py).
- [ ] **17. Accept nullable unary OpenResponses usage.** An explicit null raises `AttributeError`; the same streaming response succeeds. [Source](src/celeste/protocols/openresponses/client.py).

## Provider and modality implementations

- [ ] **18. Route synchronous OpenAI image edits to the edit endpoint.** Sync unary edit uses JSON `/images/generations`; async edit correctly uses multipart `/images/edits`. Streaming edit already routes correctly. [Source](src/celeste/modalities/images/client.py).
- [ ] **19. Honor provider `base_url` overrides.** Confirmed for DeepSeek, Mistral, and Anthropic text; inspect the same hardcoding in other media and Google transports. [Source](src/celeste/providers/deepseek/chat/client.py).
- [ ] **20. Implement Sora's advertised first-frame input.** `sora-2-pro` advertises `first_frame`, but no mapper is registered and multipart preparation is empty, so the image is warned about and dropped. [Source](src/celeste/modalities/videos/providers/openai/parameters.py).
- [ ] **21. Fix Cohere thinking-budget sentinel conversion.** On `command-a-plus-05-2026`, accepted -1/0 values become strings and are then revalidated against a numeric range. [Source](src/celeste/modalities/text/providers/cohere/parameters.py).
- [ ] **22. Serialize local xAI video-edit inputs.** Bytes/path artifacts currently become `{"video":{"url":null}}`; URL inputs work. [Source](src/celeste/modalities/videos/providers/xai/client.py).
- [ ] **23. Map OpenAI video aspect ratio without an explicit resolution.** The request currently leaks `_aspect_ratio` and produces no wire `size`. [Source](src/celeste/modalities/videos/providers/openai/parameters.py).
- [ ] **24. Correct Gradium raw-audio MIME types.** PCM, mu-law, and A-law are labeled WAV without a WAV container in unary and streaming outputs. [Source](src/celeste/providers/gradium/text_to_speech/client.py).
- [ ] **25. Surface Ollama in-band image-stream errors.** A documented `{"error":"..."}` event currently becomes an empty successful image output. [Source](src/celeste/modalities/images/providers/ollama/client.py).
- [ ] **26. Keep successful BytePlus images when a later image fails.** Final aggregation selects a trailing empty failure artifact over an earlier successful image. [Source](src/celeste/modalities/images/providers/byteplus/client.py).
- [ ] **27. Parse Google Interactions image URI delivery.** Explicit `delivery="uri"` output becomes an empty artifact and its URI is removed from metadata. [Source](src/celeste/modalities/images/providers/google/interactions.py).
- [ ] **28. Parse Google Interactions audio URI delivery.** Explicit `delivery="uri"` output raises `No audio content in response`. [Source](src/celeste/modalities/audio/providers/google/client.py).
- [ ] **29. Count Vertex output images instead of candidates.** A candidate containing two images reports one; text-only candidates can also overcount. [Source](src/celeste/modalities/images/providers/google/vertex.py).
- [ ] **30. Preserve Google embeddings usage.** The mapper discards documented `usageMetadata.promptTokenCount` values. [Source](src/celeste/providers/google/embeddings/client.py).

## Celeste skill

- [ ] **31. Select embedding models in the embedding example.** The public example reuses a TEXT model for `text.embed`, which routes to EMBEDDINGS. [Source](.agents/skills/celeste-python/references/public-api.md).
- [ ] **32. Select video-capable text-analysis models in the video-analysis example.** The public example selects a video-generation model for `videos.analyze`, which routes to TEXT. [Source](.agents/skills/celeste-python/references/public-api.md).
- [ ] **33. Include required display_name in the Model example.** Executing the current constructor example raises a validation error. [Source](.agents/skills/celeste-python/references/sdk-architecture.md).
- [ ] **34. Qualify the template-authority statement.** The architecture reference calls templates authoritative despite their defects and the main skill's source-first ordering. [Source](.agents/skills/celeste-python/references/sdk-architecture.md).
- [ ] **35. Correct the definition of modality.** Describing modality as an output family conflicts with operations such as audio transcription returning TextOutput. [Source](.agents/skills/celeste-python/references/repo-map.md).

## Secondary findings and support-contract decisions

- [ ] **36. Clarify OpenAI Live delegation configuration.** Tools select Responses delegation without its required backend model. Supply a typed configuration/default or validate an explicit raw-configuration prerequisite. [Source](src/celeste/providers/openai/live/parameters.py).
- [ ] **37. Close retained synchronous stream iterators on context exit.** A retained, partially consumed iterator keeps its source open after `with stream:` because `__exit__` is a no-op. Do not generalize to every temporary loop. [Source](src/celeste/streaming.py).
- [ ] **38. Clarify enforcement of top-level media constraints.** Transcription reaches transport with audio that its declared AudioConstraint rejects because artifact validation is a no-op. [Source](src/celeste/client.py).
- [ ] **39. Clarify OpenAI TTS PCM support.** The catalog excludes PCM although the wire mapper and upstream API support it; add support or document the intended subset. [Source](src/celeste/modalities/audio/providers/openai/models.py).
- [ ] **40. Resolve video-edit API parity.** Editing exists on the direct async client but lacks domain routing, public namespace methods, and a client sync counterpart. [Source](src/celeste/modalities/videos/client.py).
- [ ] **41. Clarify generic Chat Completions streaming usage opt-in.** Endpoints requiring `stream_options.include_usage` receive no opt-in. Keep this endpoint-specific; the Mistral allegation was withdrawn due to conflicting primary sources. [Source](src/celeste/protocols/chatcompletions/client.py).
- [ ] **42. Keep multi-choice citations with their selected answer or reject multiple choices.** With raw `n=2`, citations from another choice can be attached to the first answer; multi-choice output is not first-class. [Source](src/celeste/protocols/chatcompletions/tools.py).
- [ ] **43. Prevent streamed choices from mixing or reject multiple choices.** Streaming ignores `choice.index`, allowing interleaved choices to merge text and tool arguments. [Source](src/celeste/protocols/chatcompletions/streaming.py).
- [ ] **44. Resolve strict canonical OpenResponses assistant-content compatibility.** Assistant TextParts become `input_text`, while the canonical assistant schema expects output content. OpenAI's separate easy-input format accepts the current shape. [Source](src/celeste/modalities/text/protocols/openresponses/client.py).
- [ ] **45. Clarify BytePlus quality and aspect-ratio precedence.** Both map to `size`; quality overwrites explicit dimensions. The behavior is reproduced, but intended precedence is ambiguous. [Source](src/celeste/modalities/images/providers/byteplus/parameters.py).
- [ ] **46. Preserve BytePlus completion finish reasons.** Completion usage is retained while its finish reason can be lost. [Source](src/celeste/modalities/images/providers/byteplus/client.py).

## Verification

- [ ] **47. Exercise rendered templates together.** Render, import, instantiate, and exercise the companion templates. Item 1 adds the catalog import regression; the remaining template contracts still need coverage. [Source](tests/unit_tests).
- [ ] **48. Turn confirmed reproductions into regression coverage.** Add focused regression checks alongside each fix, preserving positive controls and the documented scope of conditional findings. [Source](tests/unit_tests).
