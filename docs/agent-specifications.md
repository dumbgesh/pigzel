# Agent Specifications

> **Status**: Baseline specification for Pigzel's three AI stage agents. Implementation begins with **Stage 1 — Creative Intelligence** (see [stage-1-creative-intelligence.md](stage-1-creative-intelligence.md)).

The three stages represent **pipeline responsibilities**, not a restriction to three individual models. Each agent communicates exclusively through validated [Data Contracts](data-contracts.md) and calls AI models via `backend/app/model_gateway`.

---

## Stage 1 — Creative Intelligence Agent (`backend/app/agents/creative`)

> **Status**: Implemented (with `MockLLMProvider`).

### Implemented Components
- **Schemas (`backend/app/schemas/creative.py`)**: `VideoFormat`, `CreativeBrief`, `CreativeConcept`, `CreativeDirection`, `CreativeIntelligencePayload`, and `CreativeIntelligenceResult`.
- **Ingestion (`backend/app/ingestion/brief_normalizer.py`)**: `normalize_brief` cleans and validates incoming `CreativeBrief` inputs.
- **Prompts (`backend/app/agents/creative/prompts.py`)**: Separated `SYSTEM_PROMPT` and `build_creative_intelligence_prompt()`.
- **Agent (`backend/app/agents/creative/agent.py`)**: `CreativeIntelligenceAgent` calls `LLMProvider`, parses JSON, validates against `CreativeIntelligencePayload` (3 unique concepts + matching `recommended_concept_id`), retries up to 2 times on validation errors, and attaches gateway provenance (`provider_name`, `model_name`, `is_mock`).
- **API (`backend/app/api/v1/creative.py`)**: `POST /api/v1/creative/concepts`.

---

## Stage 2 — Storyboard Director Agent (`backend/app/agents/storyboard`)

### Responsibilities
- Convert an approved `CreativeDirection` into a structured `Storyboard`.
- Break the narrative into ordered, independently addressable `Scene` items.
- Define `shot_type`, `camera_movement`, `lighting`, `environment`, `visual_prompt`, and `audio_cue` per scene.
- Build and maintain a consistent Visual Bible (characters, locations, color palette, style rules) across all scenes.
- Optionally generate reference images via `ModelGateway` (`image`).

### Inputs
- Approved `CreativeDirection` and `CreativeBrief`
- Optional revision `feedback` or scene edits from `Approval`

### Expected Outputs
- `Storyboard` containing `visual_bible` and ordered `Scene` list

### Human Gate
- **Approval Gate 2 (`storyboard`)**: User reviews, edits, or approves the `Storyboard` and `Scene` list before Stage 3 begins.

---

## Stage 3 — Production Planner Agent (`backend/app/agents/production`)

### Responsibilities
- Interpret the approved `Storyboard` and Visual Bible.
- Plan individual `GenerationJob` records per `Scene` (keyframes/images, video clips, voiceover, SFX, music).
- Support targeted re-planning for **scene-level regeneration** without invalidating unaffected scenes.
- Hand off completed `GeneratedAsset` clips to `backend/app/production` for FFmpeg assembly.

### Inputs
- Approved `Storyboard`
- Production/export preferences (`aspect_ratio`, target resolution, provider overrides)
- Optional target `scene_id` for scene-level regeneration

### Expected Outputs
- Ordered `GenerationJob` plan per `Scene` (leading to `GeneratedAsset` outputs and final assembled video)

### Human Gate
- **Final Review (`final_review`)**: User inspects individual clips and the assembled video, then approves for export or requests scene-level / full-video regeneration.
