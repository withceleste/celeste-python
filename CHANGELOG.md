# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

---

## [1.0.0] - 2026-10-20

200 PRs merged, 460+ files changed. First stable release: a live (realtime) modality, transcription, audio generation, upscaling, segmentation, native multimodal messages, reasoning and grounding on outputs, OpenTelemetry, and a model catalog refreshed against live provider APIs.

### 1. Live Modality (headline)

Bidirectional realtime sessions as a first-class modality.

- `celeste.live.connect(model=..., messages=..., **LiveParameters)` returns a `LiveStream`, used as `async with ... as livestream`.
- `livestream.send(...)` accepts audio (`AudioArtifact`), `ToolResult` and raw frame dicts on every model, plus `str`, `Message` and `ImageArtifact` on Gemini Live; `livestream.end()` stops sending.
- Chunks (`LiveChunk`) carry the model audio plus `transcript` and `tool_calls`; the final `LiveOutput` holds the audio artifact, `usage` and the `messages` transcript.
- **Parameters:** `voice`, `audio_format` (`LiveAudioFormat`), `tools`, `thinking_level`, `reference_images`, `temperature`, `max_tokens`, `seed` (each provider maps the subset it supports).
- **Models:** Google `gemini-3.8-live`, `gemini-3.8-live-extended-thinking` (BidiGenerateContent, also on Vertex via `GoogleADC`); OpenAI `gpt-live-1`.
- New `Modality.LIVE`, `Domain.LIVE`, `Operation.CONNECT`; `AudioMimeType.PCMU` / `PCMA`.
- PR: #477
- Files: `src/celeste/modalities/live/` (new), `src/celeste/providers/google/live/` (new), `src/celeste/providers/openai/live/` (new)

### 2. New Operations and Modalities

- **Audio transcription** — `celeste.audio.transcribe(audio, model=..., prompt=..., language=..., temperature=...)` (+ sync) returns `TextOutput`. Providers: Groq Whisper, OpenAI (`gpt-4o-mini-transcribe`, `gpt-4o-mini-transcribe-2025-12-15`, `gpt-4o-transcribe`, `gpt-4o-transcribe-diarize`, `gpt-transcribe`, `whisper-1`), ElevenLabs Scribe, Mistral Voxtral (#337, #339, #388, #413, #483, #486).
- **Audio generation** — `celeste.audio.generate(prompt, ...)` with Google Lyria (`lyria-3-clip-preview`, `lyria-3-pro-preview`, `lyria-3.5`); `reference_images` for image-conditioned music; lyrics and structure kept in `metadata["text_blocks"]` (#324, #400, #405).
- **Image upscaling** — `celeste.images.upscale(image, model=..., ...)` (+ sync) with Topaz Labs Gigapixel (8 models, async submit → status → download) and new upscale parameters (`output_width`, `face_enhancement`, `denoise`, …) (#340).
- **Segmentation modality** — `Modality.SEGMENTATION` + `Operation.SEGMENT`: `celeste.images.segment(image=..., prompt=..., model=...)` returns a `SegmentationOutput` whose `content` is `list[SegmentationMask]` (`rle`, `index`, `score`, `box`), via fal.ai SAM 3 / 3.1 with point and box prompts (#341).
- **Document input** — `celeste.documents.analyze()` and `analyze(document=...)` with `DocumentArtifact`, `DocumentMimeType` (PDF, DOCX, XLSX, PPTX, CSV, TXT, HTML, MD) on OpenAI, Anthropic, Google, Mistral and Meta; URL documents sent as `file_url` (OpenResponses) and with `mime_type` (Google) (#249, #251, #502).
- **Multimodal embeddings** — `embed()` accepts `images=`, `videos=`, `audio=`; new `celeste.images.embed()`, `celeste.videos.embed()`, `celeste.audio.embed()`; `gemini-embedding-2` (Vertex supported) (#246, #312).
- **Video editing** — Gemini Omni (`gemini-omni-flash-preview`, `gemini-omni-1.1-flash`) generate + edit; `celeste.videos.edit(...)`, sync `edit` and `client.sync.edit`; xAI `grok-imagine-video` edits accept local videos (#326, #383, #534). `gemini-omni-1.1-flash` accepts `resolution` `360p` / `720p` / `1080p` / `4k` (#505).
- **Image editing and parameters** — BytePlus Seedream `edit()` with up to 14 reference images (#508); xAI multi-image edits (#516); BFL `flux-3-image` editing and per-model input-image fields (#519); `grounding` image parameter on `flux-3-image` (#513); xAI image `quality` maps to the native `resolution` field (#507); OpenAI images gain `num_images`, `output_format`, `background`, `output_compression` and `safety_tolerance` (→ `moderation`) (#264).
- **Video parameters** — `first_frame` on xAI video models (#312); BytePlus `first_frame` / `last_frame` / reference images accept local artifacts as data URLs (#313).

### 3. Messages, Reasoning and Grounding

- **Native multimodal messages** — `Message.content` is `str | list[MessagePart]` with ordered `TextPart`, `ImagePart`, `AudioPart`, `VideoPart`, `DocumentPart`, serialized to each wire's native shape (OpenResponses, Chat Completions, Anthropic, Google, Cohere, xAI); `messages=` accepts `list[Message | ToolResult]` (#283, #312).
- **Reasoning output** — `TextOutput` and `Message` gain `reasoning` and a serializable `signature` for multi-turn thinking round-trips, `TextChunk` gains `reasoning` (Anthropic, Google, Mistral, OpenAI, xAI, Chat Completions `reasoning_content`); Anthropic adaptive-thinking summaries stream as reasoning (#254, #297).
- **`thinking_level`** — named reasoning effort is a first-class parameter on Anthropic (adaptive thinking), Google, OpenAI, xAI, DeepSeek, Groq, Mistral, Moonshot, Meta and `protocol="chatcompletions"`; `thinking_budget` is an integer token budget only (#264, #265, #295, #297, #501, #502).
- **Web-search grounding** — `Output.grounding` (`queries`, `sources`, `citations`, `search_entry_point`) on unary and streamed outputs for OpenAI, xAI, Chat Completions, Google, Anthropic and Groq compound; new `celeste.grounding` module (#287, #306, #323, #420).
- **Live tool activity** — `TextChunk.tool_activity` (`ToolActivity`, `ToolActivityStatus.STARTED` / `COMPLETED`) streams native web-search progress (#290).
- **Usage** — `TextUsage.cached_tokens`; audio and video usage gain token counts; Google embeddings report `promptTokenCount`; streamed usage completed for Anthropic, Groq and HuggingFace (#273, #300, #321, #326, #351, #534).
- **Google** — `seed` mapped on both Google text backends (#325).

### 4. Tool Calling

- **`tool_choice=`** — `ToolChoice.AUTO` / `REQUIRED` / `NONE` or a specific function, declared per model via `ToolChoiceSupport` (#253). A built-in tool as `tool_choice` raises `ValueError` instead of sending a null function name, except `WebSearch()` on OpenAI (the `allowed_tools` selector) and Anthropic (`{"type": "tool", "name": "web_search"}`) (#534).
- **`ToolOutput[Content]` / `ToolError[Content]`** — generic result types; Pydantic tool results serialized as JSON on every wire (#267).
- **Validated tool calls** — arguments for Pydantic-typed tools are validated and normalized (#278); malformed or non-object tool-call JSON raises `ValidationError` on Chat Completions, OpenResponses and Anthropic streaming instead of becoming `{}` (#534).
- **Built-in tools** — `UrlContext` on Google text models (#325); `rehydrate_tools()` rebuilds built-in tools from JSON and built-in tools gain a `kind` literal (#299); Anthropic `WebSearch` uses dynamic-filtering `web_search_20260209` on Claude 4.6+ models (#297); `ToolSupport(custom_tools=False)` for built-in-only models (#313). On the OpenResponses protocol the shared mappers now cover only `WebSearch`: `XSearch` and `CodeExecution` (sent as `code_interpreter`) move to xAI's mappers, and Ollama, OpenRouter and generic `protocol="openresponses"` raise `ValueError` for them; `CodeExecution` is unchanged on Google and Groq (#534).
- **Native replay** of provider tool turns for multi-turn loops — Anthropic thinking, server-tool and toolset blocks and code-execution containers; Google function-call ids, typed tool results and built-in steps; OpenAI stateless Responses turns; DeepSeek and Mistral reasoning; Moonshot tool names (#296, #298, #299, #309, #327, #459, #461, #462, #463, #464, #465).
- **Tool schemas** — Google sends user tools as raw JSON Schema (`parametersJsonSchema` on Vertex, `parameters` on Interactions; integer enums, `$defs`, `anyOf`) (#263, #321); response and tool schemas use Pydantic validation mode so aliases match (#534).

### 5. Google on the Interactions API

- Google text and Gemini images use `/v1beta/interactions` with an API key and Vertex `generateContent` with `GoogleADC`; TTS, Lyria and Omni video always use Interactions.
- `GoogleTextClient` and `GoogleVideosClient` become dispatchers over per-backend clients and `GoogleImagesClient` switches its backends to Interactions / Vertex; Google TTS moves from Cloud TTS to Interactions TTS and gains streaming.
- Interactions parity: streamed grounding, reasoning and cached tokens, typed tool results, `m4a` input, URI delivery for images and audio.
- `GoogleADC(location="us" | "eu")` routes Vertex to the `aiplatform.{us,eu}.rep.googleapis.com` multi-region hosts (#312).
- PRs: #312, #321, #323, #326, #327, #328, #334, #420, #435, #534

### 6. Observability (OpenTelemetry)

- Every `_predict` / `_stream` emits GenAI semantic-convention spans (`gen_ai.request.model`, `gen_ai.provider.name`, `gen_ai.usage.*`, `gen_ai.response.finish_reasons`, time to first chunk); streaming spans carry usage.
- `gen_ai.client.token.usage` and `gen_ai.client.operation.duration` histograms; opt-in message capture via `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true` (media as references, never bytes).
- `gen_ai.response.model` from the provider-reported `metadata["response_model"]`.
- New optional `[otel]` extra; no-op without it or without a `TracerProvider`.
- PRs: #270, #272, #273, #275, #277, #286, #310

### 7. Transport and Streaming

- **Retries** — `post`, `post_multipart` and `get` retry timeouts, network errors and HTTP 408/429/500/502/503/504 (2 retries, exponential backoff); streams are not retried (#288).
- **Connection lifecycle** — HTTP pools are owned per event loop and closed on shutdown; interrupted streams close their upstream iterator; Google ADC refresh runs off the event loop (#401).
- **`base_url` everywhere** — every transport (unary, streaming, polling, downloads, Vertex) builds URLs through one `_build_url(endpoint, streaming=False)`: an explicit `base_url` wins and its trailing slash is trimmed (#534).
- **Streams** — Google Interactions streams end at `interaction.completed` with no trailing delay (#496); Responses `response.incomplete` is terminal, `response.failed` raises and unfinished function calls are excluded (#401); `with stream:` closes a retained sync iterator (#534).

### 8. New Providers

- **Meta** (#502) — OpenResponses protocol, credential `MODEL_API_KEY`: `muse-wonder-1.0`, `muse-spark-1.3`, `muse-spark-1.3-contributor`.
- **OpenRouter** (#284) — OpenResponses protocol, credential `OPENROUTER_API_KEY`; any OpenRouter model slug.
- **fal.ai** (#341) — `Provider.FAL`, credential `FAL_KEY`; SAM 3 segmentation.
- **Topaz Labs** (#340) — image upscaling, credential `TOPAZ_API_KEY`.
- **New provider × modality pairs:** Groq audio (#337), Mistral audio (#339); ElevenLabs gains its speech-to-text API (#339).

### 9. New Models

**Anthropic:**
- `claude-opus-4-7` (#264); `claude-sonnet-5`, `claude-opus-4-8`, `claude-fable-5` (#293); `claude-mythos-5`, `claude-opus-5` (#360); `claude-fable-5-1`, `claude-mythos-5-1` (#384); `claude-opus-5-5` (#446); `claude-sonnet-5-5` (#468); `claude-haiku-5-5` (#495)

**OpenAI:**
- Text: `gpt-5.5`, `gpt-5.4-mini`, `gpt-5.4-nano` (#282); `gpt-5.6`, `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna` (#305); `gpt-5.3-codex`, `gpt-5.5-pro` (#312); `chat-latest` (#355); `gpt-6-astra` (#433); `gpt-6-sol`, `gpt-6-luna` (#438); `gpt-6.1-sol` (#479)
- Images: `gpt-image-2` (#264); `gpt-image-2.5-flare` (#456); `gpt-image-2.5-sunburst` (#455)
- Audio: `gpt-4o-mini-tts-2025-12-15` (#331); `gpt-4o-mini-transcribe`, `gpt-4o-transcribe`, `whisper-1` (#339); `gpt-4o-mini-transcribe-2025-12-15` (#388); `gpt-transcribe` (#413); `gpt-4o-transcribe-diarize` (#483)
- Live: `gpt-live-1` (#477)

**Google:**
- Text: `gemini-3.5-flash` (#279); `gemini-3.1-flash-lite` (GA, #281); `gemini-3.5-flash-lite`, `gemini-3.6-flash` (#330); `gemini-3.7-flash` (#347); `gemini-3.8-flash` (#391); `gemini-4-argon` (#499)
- Images: `gemini-3.1-flash-lite-image`, `gemini-3-pro-image`, `gemini-3.1-flash-image` (GA, #294); `gemini-nano-banana-2.1` (#493)
- Videos: `veo-3.1-lite-generate-preview` (#264); `gemini-omni-flash-preview` (#326); `gemini-omni-1.1-flash` (#383)
- Audio: `gemini-3.1-flash-tts-preview` (#264); `gemini-2.5-flash-preview-tts`, `gemini-2.5-pro-preview-tts` (#321); `lyria-3-clip-preview`, `lyria-3-pro-preview` (#324); `lyria-3.5` (#400); `gemini-3.8-flash-lite-tts` (#451); `gemini-3.8-flash-tts` (#452)
- Embeddings: `gemini-embedding-2-preview` (#246); `gemini-embedding-2` (#312)
- Live: `gemini-3.8-live`, `gemini-3.8-live-extended-thinking` (#477)

**xAI:**
- `grok-4.3`, `grok-4.20-0309-reasoning`, `grok-4.20-0309-non-reasoning`, `grok-imagine-image-quality` (#282); `grok-4.5` (#304); `grok-imagine-video-1.5` (#312); `grok-build-0.1`, `grok-4.20-multi-agent-0309` (#313); `grok-4.6` (#349); `grok-imagine-image-2.0` (#381); `grok-4.7` (#458)

**Mistral:**
- `mistral-medium-3-5` (#264); `mistral-large-2512`, `mistral-small-2603` (#282); Voxtral `voxtral-mini-2602`, `voxtral-mini-latest` (#339)

**Cohere:**
- `command-a-translate-08-2025`, `command-r-plus-08-2024` (#264); `command-a-plus-05-2026` (#282); `command-a-reasoning-08-2025`, `command-r-08-2024`, `c4ai-aya-vision-32b`, `c4ai-aya-expanse-32b`, `tiny-aya-global`, `tiny-aya-earth`, `tiny-aya-fire`, `tiny-aya-water` (#331)

**DeepSeek:**
- `deepseek-v4-flash`, `deepseek-v4-pro` (#265)

**Groq:**
- `qwen/qwen3.6-27b`, `minimaxai/minimax-m2.7` (#313); `qwen/qwen3.8-27b` (#350); Whisper `whisper-large-v3-turbo`, `whisper-large-v3` (#337)

**Moonshot:**
- `kimi-k2.6`, `kimi-k2.7-code`, `kimi-k2.7-code-highspeed` (#312); `kimi-k3` (#313)

**Meta:**
- `muse-wonder-1.0`, `muse-spark-1.3`, `muse-spark-1.3-contributor` (#502)

**BytePlus:**
- `dreamina-seedance-2-0-260128`, `dreamina-seedance-2-0-fast-260128` (#282, renamed in #313); `dola-seedream-5-0-pro-260628` (#302, renamed in #313); `dreamina-seedance-2-0-mini-260615` (#313); `dola-seedream-5-0-flash-260915` (#449)

**BFL:**
- `flux-2-pro-preview`, `flux-2-klein-4b`, `flux-2-klein-9b`, `flux-2-klein-9b-preview` (#313); `flux-kontext-max`, `flux-kontext-pro`, `flux-pro-1.1-ultra`, `flux-pro-1.1`, `flux-dev` (#331); `flux-3-image` (#506); `flux-3-image-klein` (#531)

**ElevenLabs:**
- `eleven_v4` (#484); Scribe `scribe_v2`, `scribe_v1` (#339); `scribe_v2_medical` (#486)

**Topaz Labs:**
- `Standard V2`, `High Fidelity V2`, `Upscale High Fidelity V3`, `Low Resolution V2`, `CGI`, `Text Refine`, `Detail`, `Transparency Upscale` (#340)

**fal.ai:**
- `fal-ai/sam-3/image-rle`, `fal-ai/sam-3-1/image-rle` (#341)

**Removed (retired, shut down or superseded on provider APIs; arrows point to the replacement):**
- Anthropic: `claude-sonnet-4-20250514`, `claude-opus-4-20250514` (#312)
- OpenAI: `dall-e-2`, `dall-e-3` (#280); `gpt-5.1-codex`, `gpt-5.2-codex`, `gpt-5.2-chat-latest` → `gpt-5.6-sol` (#432)
- Google: `gemini-3-pro-preview` (#280); `gemini-3.1-flash-lite-preview` → `gemini-3.1-flash-lite` (#281); `gemini-3-pro-image-preview` → `gemini-3-pro-image`, `gemini-3.1-flash-image-preview` → `gemini-3.1-flash-image` (#294); `gemini-embedding-001` → `gemini-embedding-2`, `veo-3.0-generate-001`, `veo-3.0-fast-generate-001` (#312); `gemini-2.5-flash-tts` → `gemini-2.5-flash-preview-tts`, `gemini-2.5-pro-tts` → `gemini-2.5-pro-preview-tts` (#321); `imagen-4.0-generate-001`, `imagen-4.0-fast-generate-001`, `imagen-4.0-ultra-generate-001` → `gemini-3.1-flash-image` (#418)
- xAI: `grok-4-0709`, `grok-4-1-fast-reasoning`, `grok-4-1-fast-non-reasoning`, `grok-4-fast-reasoning`, `grok-4-fast-non-reasoning` (#280); `grok-4.20-beta-0309-reasoning` → `grok-4.20-0309-reasoning`, `grok-4.20-beta-0309-non-reasoning` → `grok-4.20-0309-non-reasoning` (#282)
- Mistral: `open-mistral-7b`, `pixtral-12b-2409` (#280); `pixtral-large-latest`, `voxtral-mini-2507` (#311); `labs-devstral-small-2512` (#312)
- DeepSeek: `deepseek-chat`, `deepseek-reasoner` → `deepseek-v4-flash` (#314)
- Groq: `moonshotai/kimi-k2-instruct`, `moonshotai/kimi-k2-instruct-0905` (#280)
- Moonshot: `kimi-k2-0711-preview`, `kimi-k2-0905-preview`, `kimi-k2-turbo-preview`, `kimi-k2-thinking`, `kimi-k2-thinking-turbo` (#312)
- BytePlus: `seedance-1-0-lite-t2v-250428`, `seedance-1-0-lite-i2v-250428` (#280)
- ElevenLabs: `eleven_multilingual_v1`, `eleven_monolingual_v1` (#313)

### 10. Breaking Changes

- **Top-level `celeste` namespace trimmed** (#245) — internal types and specific exceptions left `celeste.__all__`, and most are no longer importable from `celeste`; import them from `celeste.exceptions`, `celeste.core`, `celeste.parameters`, `celeste.types`, `celeste.http` or `celeste.structured_outputs`.
- **Legacy APIs removed** (#310) — `Capability` / `capability=` (on `create_client()`, `register_models()`, `list_models()` and the not-found errors) → `modality=` + `operation=`; `Model.capabilities` → `Model.operations`; `APIKey` → `AuthHeader`; `web_search=` / `x_search=` / `code_execution=` → `tools=[WebSearch()]` etc.; removed without replacement: `UnsupportedCapabilityError` / `CapabilityError`, `celeste.auth.register_auth` / `get_auth_class`, `celeste.websocket`.
- **Messages** (#283) — the `Content` alias is removed; `Message.content` accepts only `str | list[MessagePart]` (wrap media in `ImagePart` etc.); `ToolResult` is no longer a `Message`; `TextOutput.message.content` is always text (typed structured output stays on `output.content`).
- **Reasoning parameters** — named efforts move from `thinking_budget` to `thinking_level` on OpenAI and xAI; `thinking_budget="high"` there is ignored with `UnsupportedParameterWarning` (#501). Google API-key text ignores `thinking_budget`; use `thinking_level` (#321). Mistral `thinking_budget` no longer maps to `prompt_mode`: `magistral-small-latest` takes `thinking_level="none"` / `"high"` and `magistral-medium-latest` has no reasoning control (#311, #501).
- **Google TTS** (#321) — requires `GOOGLE_API_KEY` (ADC alone no longer works); ids renamed to `gemini-2.5-flash-preview-tts` / `gemini-2.5-pro-preview-tts`.
- **Anthropic default `max_tokens`** (#299) — the model's ceiling (up to 128000) instead of 1024; pass `max_tokens=` to cap output.
- **Tools** — raw tool dicts with neither `type` nor `name` raise `InvalidToolError` on Anthropic, Chat Completions and OpenResponses providers (#298, #299). Invalid arguments for Pydantic-typed tools raise `ValidationError` (#278), and malformed tool-call JSON raises `ValidationError` instead of returning `{}` (#534). `XSearch` and `CodeExecution` raise `ValueError` on Ollama and generic `protocol="openresponses"`, and xAI's `CodeExecution` is sent as `code_interpreter` (#534). `WebSearch` is no longer advertised on `kimi-k2.5` (#312). Google API-key text ignores `WebSearch(blocked_domains=...)` with `UnsupportedParameterWarning`; Vertex keeps it (#517).
- **Requests** — non-streaming requests retry by default (#288); strict output schemas mark defaulted fields required (#288); an explicit `base_url` (including `""`) is now honored by every transport (#534).
- **Outputs** — `num_images > 1` returns a list of `ImageArtifact` on xAI (#374); `stream()` returns a delegating `_TracedStream` wrapper, so `isinstance(x, Stream)` checks fail (#272).
- **Voices and formats** — all 52 previous ElevenLabs voices (e.g. Rachel, Adam, George) and all 14 previous Gradium voice ids fail `VoiceConstraint` (Emma's id remains the implicit default when no voice is passed); pick from the refreshed catalogs (#308, #504). ElevenLabs' default voice is Janet instead of Rachel (#509). ElevenLabs `ulaw_8000` / `alaw_8000` output formats removed (#314).
- **Credentials** — `TOPAZLABS_API_KEY` → `TOPAZ_API_KEY` (#340).
- **Custom providers** (#401) — `APIMixin._json_headers()` is async; `_make_stream_request` is `async def` returning an unstarted `AsyncGenerator`; new `Authentication.aget_headers()`; `close_all_http_clients()` closes only the current loop's pools.
- **Utilities and typing** — `celeste.utils.build_image_data_url` → `build_data_url(artifact)` (#312); the never-mapped `prompt` key is removed from `AudioParameters` (#324).
- **Deep imports** — Google: `IMAGEN_MODELS` / `GEMINI_MODELS`, `IMAGEN_PARAMETER_MAPPERS` / `GEMINI_PARAMETER_MAPPERS`, the Imagen and Gemini image backend modules, `celeste.providers.google.cloud_tts` and the previous `celeste.providers.google.interactions` modules removed or replaced, per-backend classes renamed, `VEO_SUPPORTED_MIME_TYPES` → `GOOGLE_SUPPORTED_MIME_TYPES` (#310, #316, #321, #435). OpenAI / xAI `ThinkingBudgetMapper` → `ThinkingLevelMapper`, Mistral's removed (#501). Dead `OllamaClient` / `OllamaStream` aliases removed (#316). BFL `WidthMapper` / `HeightMapper` removed (#436). `RefResolvingJsonSchemaGenerator` / `StrictRefResolvingJsonSchemaGenerator` removed, `XSearchMapper` / `CodeExecutionMapper` moved to `celeste.providers.xai.responses.tools`, `Vertex{Provider}Endpoint` → `Vertex{Api}Endpoint` (#534).
- **Stricter constraints** (values the provider APIs already rejected) — `thinking_budget=-1` on `claude-haiku-4-5` (#297), `claude-sonnet-4-5`, `claude-opus-4-5`, `claude-opus-4-1` (#395) and `claude-opus-4-6` (#469); `thinking_level="minimal"` on `gpt-5.1`, `gpt-5.2`, `gpt-5.4`, and `"minimal"` / `"low"` on `gpt-5.2-pro`, `gpt-5.4-pro` (#394, #501); BFL edit reference limits count the primary image and raise `ConstraintViolationError` when exceeded (#436).
- **Removed models** — see section 9.

### 11. Bug Fixes

- **Structured outputs** — tool-only turns with `output_schema` keep empty content and tool calls (#534); `list[Model]` schemas keep `$defs` at the root and Cohere / Mistral stop inlining `$ref`s (no dangling refs or `RecursionError`) (#534); Anthropic sends `output_config.format` and returns empty refusals instead of raising (#428).
- **Text content** — Anthropic joins all text blocks (#428), Google Vertex all text parts (#373), OpenResponses all message items with rebased citations (#500); Cohere joins text blocks and surfaces thinking (#314); Anthropic empty `max_tokens` responses return usage instead of raising (#523); Anthropic compaction blocks preserved for replay (#430); `analyze(audio=...)` available on every text provider (#248).
- **Responses protocol** — assistant `TextPart`s replay as `output_text` (fixes OpenAI 400 on multi-turn); refusals kept in `metadata["raw_response"]["output"]`; hosted-tool billing markers kept; nullable usage objects accepted (#431, #534).
- **Usage** — `usage: null` and null token-detail objects no longer crash any parser (#534); BFL reports the settled `cost` (#426); Vertex `num_images` counts images (#534).
- **Tool calling** — Gemini mixed built-in + function tools (#285, #334); Vertex function calls without an `id` (#460); no spurious `WebSearch.kind` warning on Google Interactions (#518); Chat Completions citations from the selected choice only (#534); Vertex citation offsets mapped within their part (#401).
- **Images** — OpenAI and xAI return every generated image (#356, #374); BFL dimensions forwarded exactly, native aspect ratios, `disable_pup`, moderation and `No Card Generated` polling stops (#426, #436, #511, #512); BytePlus MIME types from `output_format` (#520), successful images kept after a later failure and the quality/aspect-ratio guard on streams (#534); sync image operations reach their endpoints (OpenAI and xAI sync edits hit `/images/edits`) and sync/stream `edit` / `upscale` raise `NotImplementedError` like async (#534); Google images dispatcher forwards `base_url`, transforms and metadata (#258, #317).
- **Audio** — ElevenLabs sends `output_format` as a query parameter (previously always MP3) with corrected MIME types and new formats (`mp3_24000_48`, `pcm_32000`, `wav_8000`…`wav_48000`) (#314); OpenAI speech MIME type from the response and `wav` output (#412); Gradium raw audio labeled `audio/pcm` / `audio/pcmu` / `audio/pcma` (#534) and `pcm_8000` (#313); Google TTS languages, `Language` gains 49 codes (#382, #414); Lyria output format and final audio block (#329, #405); audio bytes no longer copied into metadata (#307).
- **Videos** — Vertex Veo `gcsUri` parsed and download credentials scoped to Google origins (#401); Sora durations, 1080p and portrait sizes (#314).
- **Anthropic on Vertex** — `anthropic_version` in the body, `model` omitted, web search downgraded to the supported version (#515).
- **Streaming and telemetry** — streams consumed across tasks under OpenTelemetry (#277); Ollama image streams raise `StreamEventError` on in-band errors (#534); complete streamed usage and raw responses (#300).
- **Typing** — modality `Parameters` TypedDicts are `total=False` (#256); `output_schema=list[Model]` type-checks (#497).
- **Provider fixes** — DeepSeek replays `reasoning_content` (#314, #461) and its `thinking_level` mapper is no longer shadowed (#534); Cohere `thinking_budget` sentinels `-1` / `0` (#534); Moonshot `max_completion_tokens` (#312); Chat Completions serializes `VideoPart` (#312); OpenAI TTS accepts PCM (#534).
- **Catalog corrections** against live provider APIs — reasoning efforts, token limits, aspect ratios (incl. `21:9` / `5:2` on xAI images), quality tiers (incl. Seedream 4K), reference-image limits, languages, voices and streaming flags; `seedream-4-5-251128` restored (#291, #292, #297, #311, #313, #314, #331, #332, #357, #381, #385, #386, #387, #389, #390, #393, #394, #395, #396, #399, #402, #408, #436, #447, #448, #450, #453, #457, #469, #470, #471, #472, #473, #474, #475, #476, #485, #487, #489, #490, #491, #503, #522, #530).

### 12. DX Improvements

- **Parameter docs** — every modality parameter is `Annotated` with a description; `Constraint` gains an optional `description` (#261).
- **Voices** — `Voice.description`; voice catalogs refreshed from provider metadata (Gradium 66 voices, Google 30, OpenAI 13) (#308).
- **Async signatures** — async images, audio and videos operations take keyword-only `extra_body` / `extra_headers`, matching sync and stream (#534).
- **Exports** — `ImagesStream` / `ImagesStreamNamespace` and `AudioStream` / `AudioStreamNamespace` exported from their modality packages (#534).
- **Templates** — provider, modality and protocol templates render and import with only their TODO fill-ins and pass type-check (a new modality also adds the documented mypy override); new aggregator `models.py` template (#534).
- **Contributing** — protocol-provider, model-catalog, model-removal, second-API and new-modality playbooks in CONTRIBUTING; `CLAUDE.md` and the `celeste-python` agent skill (#283, #315, #318, #477, #534).
- **Notebooks** — `notebooks/multimodal-embeddings.ipynb` (#246).

### 13. Architecture (Internal)

- **Base modality operations** — `generate()`, `analyze()`, `speak()`, `edit()` centralized on modality clients via endpoint ClassVars; -300 lines (#248).
- **Multi-backend dispatchers** — Google text, images and videos and ElevenLabs audio select a backend once and delegate every hook; enforced by `test_dispatcher_delegation.py` (#317, #321, #326, #339).
- **Protocol mapper reuse** — protocol mapper lists shared by compatible providers; vendor overrides listed explicitly (#252, #534).
- **Composition conventions** — `{Provider}{Api}Mixin` aliases and plain `config` imports (#316).
- **Stream hooks** — `_aggregate_raw_response` (#300), `_is_terminal_event` (#496), `_parse_chunk_transcript` / `_parse_chunk_tool_calls` (#477); `HTTPClient.stream_post_bytes` (#480).

### 14. Testing

- **Suite consolidated** around public contracts and parametrized provider matrices (-7,989 test lines); arbitrary unregistered provider model ids remain supported and optimistically advertise streaming (#310).
- **742 unit tests** at release (527 in v0.11.0); coverage now measures provider, protocol and modality code (omit list removed) with a 65% gate (was 80%) (#310).
- **Locked dependencies** — `uv.lock` committed; CI, type-check, test and publish install with `uv sync --locked`; daily latest-deps canary and weekly Dependabot lockfile updates (#498); mypy pinned below 2.4 (#494).

---

## [0.11.0] - 2026-03-27

55+ PRs merged, 400+ files changed.

### 1. Tool Calling (v0.11.0 — headline)

Unified tool calling across all providers — the bridge between LLM reasoning and real-world action.

- Single `tools=` parameter replaces `web_search=True`, `x_search=True`, `code_execution=True`.
- **Three tool shapes:**
  - **Built-in tools** (server-side, provider-mapped): `WebSearch(blocked_domains=["reddit.com"])`, `XSearch()`, `CodeExecution()`
  - **User-defined function tools** (dict with `name` + `parameters`): `{"name": "get_weather", "parameters": WeatherParams}`
  - **Raw passthrough** (dict without `name`): `{"type": "bash_20250124"}` — escape hatch for provider-specific tools
- **New types:** `Tool`, `WebSearch`, `XSearch`, `CodeExecution`, `ToolCall`, `ToolResult`, `ToolDefinition`
- **Multi-turn tool use** via `ToolResult(Message)` — tool results are messages in the conversation array.
- **Streaming tool calls** — tool call deltas accumulate during streaming, reconstructed into `ToolCall` objects after stream exhaustion.
- **Architecture:** `ToolMapper` per tool type per provider (parallel to `ParameterMapper`). `ToolsMapper` dispatches by tool type. `ToolSupport` constraint on models declares which built-in tools are supported.
- **Deprecated param shims** — `web_search=True` still works with `DeprecationWarning`, removal date 2026-06-07.
- **Philosophy:** Celeste is primitives, not a framework. Tools are a parameter — celeste passes schemas to providers, normalizes responses into `ToolCall` objects, and returns them. It never auto-executes.
- PRs: #199, #228, #229, #232, #234, #235
- Files: `src/celeste/tools.py` (new), provider `tools.py` files (6 new), `tests/integration_tests/text/test_tools.py` (new)

### 2. Protocol Layer (v0.10.0)

Extracted shared protocol implementations from provider-specific code. Providers now inherit protocol base classes and override only what differs.

- **ChatCompletions protocol** (`protocols/chatcompletions/`) — shared `/v1/chat/completions` implementation. Used by: DeepSeek, Groq, HuggingFace, Mistral, Moonshot.
- **OpenResponses protocol** (`protocols/openresponses/`) — shared Responses API implementation. Used by: OpenAI, xAI, Ollama.
- **`protocol=` + `base_url=` parameters** (v0.11.0, #241) — connect to any compatible API (vLLM, Ollama, MiniMax, LocalAI) without a registered provider. Protocol is wire format identity, not company name.
- **~2000 lines of provider code deduplicated** across 34 files. Provider clients went from ~140 lines to ~10-30 lines.
- Each protocol provides: `client.py`, `config.py`, `parameters.py`, `streaming.py`, `tools.py`.
- PRs: #153, #154, #241
- Files: `src/celeste/protocols/` (new directory)

### 3. Vertex AI (v0.10.0)

Route requests through Google Vertex AI for any supported provider.

- `GoogleADC` auth with `project_id` and `location` fields.
- All Google providers routable through Vertex AI (text, images, embeddings, video, TTS).
- Cross-provider support: Anthropic, Mistral, and DeepSeek on Vertex AI.
- `_make_poll_request` for long-running operations (video generation).
- `google-auth` moved to optional `[gcp]` extra (#133) — saves ~24.5 MB for non-GCP users.
- 39 unit tests for URL routing in `test_vertex_routing.py`.
- PR: #135
- Files: `src/celeste/auth.py`, all provider clients

### 4. New Providers

- **HuggingFace** (v0.10.2, #183) — OpenAI-compatible inference router (`router.huggingface.co`), 127+ models across 15 inference providers. Uses ChatCompletions protocol. Credential: `HF_TOKEN`.
- **xAI Grok Imagine** (v0.9.6, #128) — Image generation (`grok-imagine-image`) and video generation (`grok-imagine-video`) with aspect ratios, num_images, duration, resolution. Async polling for video.
- **Ollama Images** (v0.9.4, #119) — Local image generation via `/api/generate`. Flexible parameter validation (pass-through for dynamic providers). Adds `NEGATIVE_PROMPT` parameter.
- **OpenResponses + Ollama Text** (v0.9.4, #111) — `Provider.OPENRESPONSES` for Responses-compatible APIs, `Provider.OLLAMA` for local inference. `NoAuth` for local providers, `base_url=` for custom gateways.
- Files: `src/celeste/providers/huggingface/`, `src/celeste/providers/xai/images/`, `src/celeste/providers/xai/videos/`, `src/celeste/providers/ollama/`

### 5. New Models

**Anthropic:**
- Claude Opus 4.6 (#130) — 64K max tokens, 32K thinking budget
- Claude Sonnet 4.6 (#179) — 64K max tokens, extended thinking

**Google:**
- Gemini 3.1 Pro Preview (#179) — thinking levels: low/medium/high
- Gemini 3.1 Flash Lite Preview (#213)

**OpenAI:**
- GPT-5.4, GPT-5.4 Pro (#213) — thinking budget + verbosity

**xAI:**
- Grok 4.20 Beta (reasoning + non-reasoning) (#213)

**BytePlus:**
- Seedream 5.0 Lite (#181) — 2K/3K quality tiers, 16 resolution presets

**Moonshot:**
- Kimi K2.5 — with WebSearch tool support

**Removed (no longer available on provider APIs, #243):**
- OpenAI: GPT-4, GPT-4 Turbo, GPT-3.5 Turbo
- xAI: Grok 2 Vision 1212
- Groq: Llama 4 Maverick 17B 128E

### 6. Multi-turn Conversations (v0.9.4)

First-class support for multi-turn conversations across all text providers.

- `Message(role, content, tool_calls)` and `Role` (USER, ASSISTANT, SYSTEM, DEVELOPER) types.
- All text entrypoints accept `messages=` parameter for conversation history.
- Provider normalization: Anthropic system messages extracted to top-level, Google system_instruction, chat vs responses arrays.
- PR: #111
- Files: `src/celeste/types.py`, all text provider clients

### 7. Breaking Changes

- **`web_search=`/`x_search=`/`code_execution=` deprecated** — replaced by `tools=[WebSearch()]`. Old boolean params work via shims with `DeprecationWarning` until 2026-06-07.
- **`google-auth` moved to optional extra** (#133) — `pip install "celeste-ai[gcp]"` required for Vertex AI. Raises `MissingDependencyError` with install instructions if missing.
- **`requests` removed from runtime deps** (#132) — only needed as `google-auth[requests]` transport.
- **Deprecated models removed** (#243) — GPT-4, GPT-4 Turbo, GPT-3.5 Turbo, Grok 2 Vision 1212, Llama 4 Maverick (all dead on provider APIs).
- **`_parse_content` signature change** (#203) — now `(self, response_data) -> Content`, no `**parameters`. Affects custom provider subclasses.
- **`FieldMapper.name` type change** (#161) — from `StrEnum` to `ClassVar[StrEnum]`. Affects custom `ParameterMapper` subclasses.
- **`ModalityClient` constructor** (#241) — gained `protocol=` and `base_url=`; `provider` became `Provider | None`.

### 8. Bug Fixes

- **BlockingPortal thread leak** (#239) — sync stream iteration leaked portal thread on exception, `break`, or abandonment. Rewrote `__iter__` as generator with `try/finally` for guaranteed cleanup. Fixed CI hanging 19 minutes after tests.
- **SSE stream error detection** (#192) — mid-stream errors (Anthropic `overloaded_error`, OpenAI `server_error`) now raise `StreamEventError` instead of being silently discarded.
- **Streaming HTTP error enrichment** (#196) — consistent provider-enriched error messages across streaming and non-streaming paths.
- **`json.loads` strict mode** (#152) — LLM-generated content with literal `\n` in thinking fields caused `Invalid control character` errors. Fixed with `strict=False` in all 8 provider `parse_output` methods.
- **`UnicodeDecodeError` in error handler** (#171) — binary error bodies (e.g. `0xff`) escaped the catch block.
- **`_parse_usage` return type mismatch** (#174) — 3 modality-level overrides returned typed objects instead of `RawUsage` dicts, crashing on Gemini/Imagen.
- **Streaming image edits routed to wrong endpoint** (#180) — OpenAI streaming edits sent to `/v1/images/generations` instead of `/v1/images/edits`.
- **Empty/whitespace credentials** (#190) — now raises `MissingCredentialsError` instead of sending empty API keys.
- **API key whitespace causing HTTP errors** (#116) — strip whitespace from API keys to prevent `LocalProtocolError: Illegal header value`.
- **Null `tool_calls` in ChatCompletions streaming** — DeepSeek sends `"tool_calls": null` instead of omitting the key. `.get("tool_calls", [])` returns `None` when key exists with null value. Fixed with `or []`.
- **Pydantic V2.11 deprecation** — `tool.model_fields` on instance changed to `type(tool).model_fields` (class access) in 4 tool mapper files.

### 9. DX Improvements

- **`extra_body=` on all modalities** (#126) — pass provider-specific fields into the request body on images, audio, videos, embeddings.
- **`extra_headers=` on all client methods** (#193) — `generate`, `stream`, `analyze`, `speak`, `embed`, `edit` all accept `extra_headers: dict[str, str] | None`.
- **`auth=` passthrough on all namespace methods** (#146) — previously only async text generation passed it through, silently dropping it elsewhere. Vertex AI auth now works across all domains.
- **`UnsupportedParameterWarning`** (#212) — warns when parameters are silently ignored by a provider instead of failing silently.
- **`InvalidToolError`** (#228) — immediate error for bad tool list items (e.g., `tools=[WebSearch]` without `()`, strings, integers).
- **WebSearch config field drop warnings** (#235) — warns when fields like `blocked_domains` or `max_uses` aren't supported by the provider.
- **Base64 serialization** (#145) — `ser_json_bytes="base64"` on Output/Chunk models ensures `model_dump_json()` correctly base64-encodes artifact data.
- **Colab quickstart notebook** (#115) — `notebooks/celeste-colab-quickstart.ipynb`.
- **CONTRIBUTING.md rewrite** (#131) — accurate workflow documentation.

### 10. Architecture (Internal)

- **FieldMapper base class** (#161) — replaces repeated validate-then-set pattern across 45 mapper classes with 2-line declarations.
- **`_content_fields` ClassVar** (#160) — replaces 20 identical `_build_metadata()` overrides with one-line declarations. -215 lines.
- **Generic `MediaConstraint`** (#176) — 6 near-identical media constraint classes (~190 lines) replaced with two generic bases.
- **Stream base class consolidation** (#168, #172) — `_parse_chunk_content`/`_wrap_chunk_content` hooks. 6 text provider streams became empty classes. -521 lines total.
- **`ParameterMapper` generic on Content** (#189) — PEP 695 generics, end-to-end type safety.
- **`_transform_output` moved to base `_predict`** (#187) — prevents silent structured output failures in new providers.
- **`_json_headers()` helper** (#162) — replaces verbatim auth + Content-Type header construction across every provider client.
- **Artifact validator handles base64** (#139) — removed manual `base64.b64decode()` across 6 provider clients.
- **ChatCompletionsTextClient protocol base** (#199) — modality-level protocol class that DeepSeek, Groq, HuggingFace, Mistral, Moonshot inherit from.
- **Provider-level OpenResponses removed** (#229) — OpenAI/xAI/Ollama now use protocol-level `OpenResponsesTextClient`. -396 lines.

### 11. Testing

- **+882 lines of new tests** across unit and integration suites.
- Integration tests for tools: 17 parametrized runs across 4 providers (Anthropic, OpenAI, Google, xAI) — WebSearch, streaming, function tools, XSearch, multi-turn ToolResult round-trip.
- Vertex AI routing tests: 39 tests covering URL routing for all provider/modality combinations.
- Protocol base URL tests: 185 lines (`test_protocol_base_url.py`).
- Streaming tests expanded: +246 lines, sync iteration cleanup tests.
- Exception tests: `InvalidToolError`, `StreamEventError`.
- Client tests: unsupported parameter warnings, deprecated param shims.
- Constraint tests: `ToolSupport` validation (5 tests).
- Test count: ~478 → 527+.

### Contributors

- @Leo-le-jeune — HuggingFace text generation provider (#183)
- @Seluj78 and @Olaiwonismail — CONTRIBUTING.md rewrite (#131)
- @Alistorm and @XinyueZ — design input on the tool calling architecture (#150)

---

## [0.9.1] - 2026-01-17

279 files changed. Monolith rewrite — single package, modality-first architecture.

### Packaging Rationale (Monolith)
- DX first: pip install celeste-ai is the only thing most users want to remember. Requiring extras like celeste-ai[text] adds cognitive load and drops adoption.
- Lightweight anyway: importing modalities/providers doesn’t add “weight” in practice. The package stays tiny (under ~2 MB), and 90% of the code is core no matter what.
- No heavyweight vendor SDKs: Celeste uses lightweight HTTP clients, so “bundling providers” doesn’t drag in massive dependencies.
- Faster + cleaner: removing the registry/entry‑points means fewer indirections, no dynamic discovery, and faster startup with clearer behavior.
- Simpler maintenance: one package, one version, one release pipeline. Fewer moving parts and fewer “what do I install?” support tickets.
- Predictable behavior: providers are always available; no hidden runtime failures because a plugin wasn’t installed.
- Better UX in docs: one install step + one API surface; examples “just work.”

### Packaging Changes
- Removed the legacy multi-package workspace and extras-only install paths.
- Now ships as a single PyPI package (`celeste-ai`).
- Updated dependency and tooling configuration to the monolith layout (tests/coverage/mypy/ruff paths now target `src` and `tests` only).
- File updated: `pyproject.toml`.
- File updated: `Makefile`.
- Files deleted: `packages/` (all legacy capability/provider packages and their tests).

### Tests
- Added modality-first integration tests (`tests/integration_tests/**`) covering generate/edit/analyze/speak and streaming flows per modality.
- Added media fixtures for image/audio/video analysis in integration tests.
- Expanded unit tests for namespace routing, modality inference, stream metadata, auth/credentials registry, artifact handling, and IO validation.
- Replaced legacy package-based tests with a unified monolith test layout.
- Files added: `tests/integration_tests/**`, `tests/testing_guidelines.md`, `tests/unit_tests/utils/**`, `tests/__init__.py`.
- Files updated: `tests/unit_tests/*.py`.
- Files removed: legacy package-specific test suites under `packages/**`.

### CI/CD
- CI workflow now targets monolith paths only (`src/celeste`, `tests`) for ruff, mypy, and bandit.
- Publish workflow runs required integration tests from `tests/integration_tests` and no longer uses package-based change detection.
- Build step produces a single package (`uv build`) before TestPyPI → PyPI → GitHub release.
- Files updated: `.github/workflows/ci.yml`, `.github/workflows/publish.yml`.

### Feature Highlight: `extra_body` passthrough
- New `extra_body` parameter lets you pass provider-specific fields or arbitrary JSON into the request body.
- This unblocks new provider capabilities before Celeste adds first-class parameter mapping.
- Implemented via deep-merge into the built request payload.
- File updated: `src/celeste/client.py`.

### Architecture Shift: Modalities
- v1 moves from capability-centric clients (one method) to modality-centric clients (one output type). Modality = output type (text/images/audio/video/embeddings), operations become methods (`generate`, `edit`, `analyze`, `embed`).
- Domain is the resource you work with (e.g., videos), regardless of whether the input is text or media; modality is what comes out (output type). This clarifies why one client can expose multiple operations while still being type-safe.
- Namespaces are domain-first (the resource you work with); `create_client` is modality-first (the output type you want). Routing uses (domain, operation) → modality.
- Cross-domain operations are explicit: image/audio/video analysis always routes to the text modality; embeddings always route to the embeddings modality.
- Operations exposed: text `generate`/`embed`, images `generate`/`edit`/`analyze`, audio `speak`/`analyze`, videos `generate`/`analyze`.
- Files added: `src/celeste/modalities/` (text/images/audio/videos/embeddings submodules).

### Namespace API
- Domain namespaces (`celeste.text`, `celeste.images`, `celeste.audio`, `celeste.videos`) provide one-line calls that route to the correct modality/operation under the hood.
- Domain indicates the resource you work with, even if the input is different (e.g., video generation can take text input but stays in the videos domain). Modality indicates the output type (e.g., `celeste.images.analyze(...)` routes to the text modality because analysis returns text).
- The namespace pattern is more discoverable (IDE autocomplete) and matches how people think: start from the domain, then pick the action.
- Execution modes are explicit via namespace properties: async by default, with `.sync` and `.stream` for blocking and streaming workflows.
- The factory pattern remains available for explicit configuration and client reuse when you want full control.
- Files added: `src/celeste/namespaces/__init__.py`, `src/celeste/namespaces/domains.py`.

### Providers
- Added monolith provider layer under `src/celeste/providers/` with per-provider config/parameters/streaming modules.
- Provider modules include: OpenAI (responses/images/audio/videos), Google (generate_content/imagen/veo/cloud_tts/embeddings/interactions), Anthropic (messages), Cohere/Mistral/DeepSeek/Groq/Moonshot (chat), xAI (responses), ElevenLabs/Gradium (text_to_speech), BFL/BytePlus (images + videos).
- Central provider exports in `providers/__init__.py` for import/discovery.
- Added provider API references doc at `src/celeste/providers/api_references.md`.
- Files added: `src/celeste/providers/**` and `src/celeste/providers/__init__.py`.

### Contributor Templates
- Added code generation templates for contributors to easily add new modalities, providers, or parameters.
- Templates follow the monolithic architecture with proper relative imports and type patterns.
- **Modality templates** (`templates/modalities/`): Full scaffolding for new output types including client, IO types, parameters, streaming, provider implementations, and integration tests.
- **Provider API templates** (`templates/providers/`): Scaffolding for new provider HTTP clients including config, client mixin, streaming, and parameter mappers.
- Templates include: `client.py`, `io.py`, `parameters.py`, `streaming.py`, `models.py`, `config.py`, and test files.
- Placeholder conventions: `{Modality}` (PascalCase), `{modality}` (lowercase), `{Provider}`, `{provider}`, `{Api}`, `{api}`, `{Content}`.
- Files added: `templates/modalities/**`, `templates/providers/**`.

### API Wiring
- Updated public exports to v1 surface, including modalities, operations, clients, structured outputs, and namespace singletons.
- Added modality/provider client map and auto-registered modality models at import time.
- Added capability-to-(modality, operation) translation layer to keep `capability` supported with a deprecation warning.
- `create_client` now supports modality + operation arguments, infers operations when possible, and resolves models with better modality-aware errors.
- File updated: `src/celeste/__init__.py`.

### Docs
- Updated Quick Start and multimodal examples to the namespace‑first v1 API.
- Added a Namespace API section and an “Advanced: create_client” section.
- Added “Behavior changes since v0.3.9”.
- Replaced extras installs with a single‑package install (`pip install celeste-ai` / `uv add celeste-ai`).
- Updated the PyPI badge and added the v1 beta callout banner.
- File updated: `README.md`.

### Release Prep
- Set package version to `0.9.1` for the public v1 beta.
- Updated development status classifier to Beta.
- Removed notebook/scraping-only runtime deps from install requirements (ipykernel, matplotlib, beautifulsoup4).
- File updated: `pyproject.toml`.


### Client Core / Modality Architecture (`src/celeste/client.py`)
- Replaced the capability-specific `Client` with a unified `ModalityClient` base class.
- Removed the capability/provider client registry and related lookup helpers.
- Added `modality` as a first-class field and use it for HTTP client selection.
- Added `sync` and `stream` namespace properties for modality clients.
- `_predict` now takes explicit `inputs` plus optional `endpoint` and `extra_body`, and expects provider `_make_request` to return a response data dict (not an `httpx.Response`).
- `_stream` now takes explicit `inputs` and a `stream_class`, passes `client=self`, and supports `extra_body` + `streaming=True`.
- Added `APIMixin._deep_merge` and extended `_build_request` to merge `extra_body` into the request body.
- Removed capability compatibility validation at init time.
- Updated content types to `TextContent` / generic `Content` and adjusted `_transform_output` accordingly.
- Metadata now includes `modality` and the raw response payload.
- File updated: `src/celeste/client.py`.

### Auth + Credentials (`src/celeste/auth.py`, `src/celeste/credentials.py`)
- Renamed `APIKey` to `AuthHeader` (with `secret`, `header`, `prefix`), keeping `APIKey` as a backwards-compatible alias.
- `get_auth_class` no longer auto-loads providers from entry points; auth types must be registered explicitly.
- Replaced static provider maps with dynamic auth registry (`register_auth`, `get_auth_config`).
- Added credential fields for `MOONSHOT_API_KEY`, `DEEPSEEK_API_KEY`, and `GROQ_API_KEY`.
- `get_auth` now instantiates custom auth classes or builds an `AuthHeader` from the registry.
- `has_credential` returns true for auth-class providers; `list_available_providers` now filters by registry + credentials.
- Files updated: `src/celeste/auth.py`, `src/celeste/credentials.py`.

### Artifacts + MIME (`src/celeste/artifacts.py`, `src/celeste/mime_types.py`)
- Added `get_bytes()` and `get_base64()` primitives for content access.
- Removed `_default_mime_type` and `to_data_url()` (moved to utilities).
- Added `src/celeste/utils/mime.py` with `detect_mime_type()` and `build_image_data_url()`.
- MIME detection uses `filetype` library (magic bytes).
- Added JSON serialization for `data: bytes` using base64.
- Files updated: `src/celeste/artifacts.py`, `src/celeste/mime_types.py`.
- Files added: `src/celeste/utils/`.

### HTTP + WebSocket (`src/celeste/http.py`, `src/celeste/websocket.py`)
- Switched shared client registries to use `Modality` instead of `Capability`.
- HTTP client now recreates the `httpx.AsyncClient` if the event loop changes to avoid "Event loop is closed" errors.
- Files updated: `src/celeste/http.py`, `src/celeste/websocket.py`.

### Streaming (`src/celeste/streaming.py`)
- Added sync iteration support via anyio blocking portals (`__iter__`, `__next__`).
- Added sync context manager support (`__enter__`, `__exit__`) with portal cleanup.
- Added `_build_stream_metadata` hook (default: raw events).
- Stream exhaustion no longer raises `StreamEmptyError` when no chunks were produced.
- Improved cleanup: guard `aclose` during active iteration and suppress close-time runtime errors.
- File updated: `src/celeste/streaming.py`.

### Exceptions (`src/celeste/exceptions.py`)
- `ModelNotFoundError` now supports modality-based messages.
- `ClientNotFoundError` expanded to include modality + operation.
- Added `ModalityNotFoundError`.
- File updated: `src/celeste/exceptions.py`.

### Behavior Changes / Notes
- Provider `_make_request` now returns a response data dict; error handling is expected inside provider implementations.
- Empty streams no longer raise `StreamEmptyError` on exhaustion.
- Auth types are no longer auto-loaded from entry points; they must be registered explicitly.
- Related files: `src/celeste/client.py`, `src/celeste/streaming.py`, `src/celeste/artifacts.py`, `src/celeste/auth.py`.

---

[Unreleased]: https://github.com/withceleste/celeste-python/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/withceleste/celeste-python/compare/v0.11.0...v1.0.0
[0.11.0]: https://github.com/withceleste/celeste-python/compare/v0.9.1...v0.11.0
[0.9.1]: https://github.com/withceleste/celeste-python/compare/v0.3.9...v0.9.1
