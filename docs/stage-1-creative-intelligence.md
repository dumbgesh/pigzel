# Stage 1 Specification — Creative Intelligence

> **Status**: Implementation-ready specification for Milestone 2 (`backend/app/agents/creative`).

## 1. Purpose

The **Creative Intelligence Agent** transforms a validated `CreativeBrief` (and any ingested reference context) into **three distinct creative concepts** and a **recommended creative direction**, returning schema-validated output ready for Human Approval Gate 1.

---

## 2. Input Brief Structure (`CreativeBrief`)

Normalized by `backend/app/ingestion` before reaching the agent:

- **Required**:
  - `idea` (`str`, non-empty, trimmed, e.g., min 10 chars, max 4000 chars)
  - `format` (`ad | social | promo | explainer | short_film | brand_film | custom`)
- **Optional (with sensible defaults for Simple Mode)**:
  - `target_duration_seconds` (`int | None`, must be `> 0` and `<= 1800` if provided)
  - `aspect_ratio` (`str`, default `"16:9"`, e.g. `"16:9"`, `"9:16"`, `"1:1"`, `"4:5"`)
  - `target_audience` (`str | None`)
  - `tone` (`str | None`)
  - `constraints` (`list[str]`, default `[]`)
  - `reference_notes` (`list[str]`, default `[]`)
  - `reference_asset_uris` (`list[str]`, default `[]`)

### Reference Material & Context
- Text notes, brand guidelines, and links/URIs to uploaded reference files are normalized by `backend/app/ingestion` into `reference_notes` and `reference_asset_uris`.
- For Milestone 2, text-based `reference_notes` are injected directly into the structured prompt context; `reference_asset_uris` are preserved in the brief metadata for multimodal/downstream use.

---

## 3. Expected Output Structure (`CreativeIntelligenceResult`)

The agent returns a single validated Pydantic v2 object containing:

1. **`concepts`**: `list[CreativeConcept]` — **exactly 3** distinct concepts:
   - `id` (`str`, e.g. `"concept_1"`, `"concept_2"`, `"concept_3"`)
   - `title` (`str`, concise title)
   - `premise` (`str`, core creative hook)
   - `narrative_arc` (`str`, beginning → middle → end)
   - `visual_style` (`str`, visual aesthetic & mood)
   - `audio_style` (`str`, voiceover/music/SFX direction)
   - `rationale` (`str`, why it satisfies the brief)
2. **`direction`**: `CreativeDirection` — the recommended direction:
   - `selected_concept_id` (`str`, must match one of the 3 `concepts[i].id` values)
   - `narrative_summary` (`str`)
   - `pacing_guidance` (`str`)
   - `visual_guidelines` (`str`)
   - `audio_guidelines` (`str`)
   - `production_instructions` (`list[str]`, `>= 1` actionable items for Stage 2 & 3)

### Three Distinct Concepts Requirement
- Prompts and validation must ensure the 3 concepts explore genuinely different creative angles (e.g., different narrative framing, emotional tone, or visual treatment) rather than minor wording variations.
- Concept `id`s and `title`s must be unique within the response.

---

## 4. Validation Requirements

Enforced via Pydantic v2 in `backend/app/schemas`:
- `len(concepts) == 3`
- All `concept.id` values are unique and non-empty.
- All `concept.title` values are unique (case-insensitive) and non-empty.
- `direction.selected_concept_id` **must** exist in `{c.id for c in concepts}`.
- `len(direction.production_instructions) >= 1`, with no empty strings.
- All required string fields are stripped and non-empty.

---

## 5. Error Handling

| Failure Mode | Handling Strategy |
| :--- | :--- |
| **Invalid `CreativeBrief` input** | Rejected in Ingestion/API layer with HTTP `422` and structured field errors. |
| **LLM returns invalid JSON or fails Pydantic validation** | Agent performs up to **2 bounded retries**, appending the exact validation error to guide correction. If still invalid, raises `AgentOutputValidationError`. |
| **Provider timeout / rate limit / 5xx** | `ModelGateway` raises normalized `ProviderTransientError` (or `ProviderAuthError` / `ProviderConfigError`). Orchestrator marks version/step `failed` with traceable error metadata; no silent fallback to fake data in production. |

---

## 6. Human Approval Requirements

- When Stage 1 completes, `ProjectVersion.current_stage` transitions to `approval_1`.
- Stage 2 (`Storyboard Director Agent`) **cannot** run until an `Approval` record with `gate="creative_direction"` and `decision="approved"` exists for that `ProjectVersion`.
- **Approval Actions**:
  1. **Approve**: Optionally override `selected_concept_id` if the user prefers one of the other 2 concepts; unlocks Stage 2.
  2. **Request Revision**: Submits `feedback` (`str`); Orchestrator creates a new `ProjectVersion` (`parent_version_id` set), passes the prior output + `feedback` to Stage 1, and returns to `approval_1`.
  3. **Reject**: Marks the version `rejected`/`failed` without advancing.

---

## 7. Provider Abstraction (`backend/app/model_gateway/llm`)

Keep the abstraction minimal and typed (using `typing.Protocol`):

```python
class LLMProvider(Protocol):
    provider_name: str

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_schema: type[T],
        model: str | None = None,
        temperature: float = 0.7,
    ) -> LLMResponse[T]: ...
```

- **MockLLMProvider**: Deterministic in-memory provider for unit and integration tests (no network calls, no API keys).
- **OpenAICompatibleLLMProvider**: Lightweight `httpx.AsyncClient` adapter supporting hosted open-weight inference APIs and local OpenAI-compatible servers via `PIGZEL_LLM_BASE_URL`, `PIGZEL_LLM_API_KEY`, and `PIGZEL_LLM_MODEL`.
- No heavy LLM orchestration frameworks (e.g., LangChain, LlamaIndex, CrewAI) are used.
