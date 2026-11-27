# Architecture

> **Status**: Finalized baseline architecture. Components described below define the target modular design and strict boundaries; implementation begins in Milestone 2.

## High-Level Overview

Pigzel is a modular, schema-driven pipeline that separates **input ingestion**, **creative reasoning**, **visual planning**, **production planning**, **media processing**, **orchestration**, **storage**, and **model inference** into distinct layers with explicit data contracts.

```text
+-----------------------------------------------------------------------+
|                         Frontend (Next.js)                            |
|                  Simple Mode  |  Advanced Mode                        |
+-----------------------------------+-----------------------------------+
                                    | HTTP / JSON
+-----------------------------------v-----------------------------------+
|                       API Layer (backend/app/api)                     |
+-----------------------------------+-----------------------------------+
                                    |
        +---------------------------+---------------------------+
        v                                                       v
+-------+-------------------+                       +-----------+-----------+
| Input & Context Ingestion |                       | Workflow Orchestrator |
| (backend/app/ingestion)   |                       | (app/orchestrator)    |
+-------+-------------------+                       +-----------+-----------+
        |                                                       |
        +---------------------------+---------------------------+
                                    |
        +---------------------------+---------------------------+
        v                           v                           v
+-------+-------------+   +---------+---------+   +-------------+-------+
| Creative Intel.     |   | Storyboard        |   | Production Planner  |
| Agent               |   | Director Agent    |   | Agent               |
| (agents/creative)   |   | (agents/storyboard|   | (agents/production) |
+-------+-------------+   +---------+---------+   +-------------+-------+
        |                           |                           |
        +---------------------------+---------------------------+
                                    |
+-----------------------------------v-----------------------------------+
|                  Model Gateway (backend/app/model_gateway)            |
|          LLM       |       Image       |       Video     |   Audio    |
+-----------------------------------+-----------------------------------+
                                    |
        +---------------------------+---------------------------+
        v                                                       v
+-------+-------------------+                       +-----------+-----------+
| Production & Media Proc.  |                       | Storage & Asset Mgmt. |
| (backend/app/production)  |                       | (backend/app/storage) |
+---------------------------+                       +-----------------------+
```

---

## Component Responsibilities and Boundaries

### 1. Creative Intelligence Agent (`backend/app/agents/creative`)
- **Responsibilities**:
  - Interpret the normalized `CreativeBrief` and ingested reference context.
  - Generate three distinct `CreativeConcept` options.
  - Produce a recommended `CreativeDirection` with narrative arc, tone, messaging, and high-level production instructions.
  - Revise concepts/direction when given human feedback.
- **Boundaries**:
  - Does **not** break stories into individual camera shots or storyboards.
  - Does **not** call vendor SDKs directly; uses `ModelGateway` LLM interface only.
  - Does **not** manage project persistence or approval state.

### 2. Storyboard Director Agent (`backend/app/agents/storyboard`)
- **Responsibilities**:
  - Convert an approved `CreativeDirection` into an ordered `Storyboard` of `Scene` items.
  - Define shot types, camera movements, lighting, environments, pacing, visual prompts, and audio cues per scene.
  - Maintain a consistent Visual Bible (recurring subjects, environments, palette, style rules) across all scenes.
  - Optionally generate visual reference frames via `ModelGateway` image interface.
- **Boundaries**:
  - Does **not** modify the approved `CreativeDirection` without a Stage 1 revision.
  - Does **not** dispatch video/audio rendering jobs or assemble final video files.

### 3. Production Planner Agent (`backend/app/agents/production`)
- **Responsibilities**:
  - Translate an approved `Storyboard` into concrete `GenerationJob` specifications (image-to-video, text-to-video, voiceover, SFX, music) per scene.
  - Select appropriate capability parameters and dependencies between jobs (e.g., keyframe before video clip).
  - Support targeted re-planning for single-scene regeneration.
- **Boundaries**:
  - Does **not** execute FFmpeg assembly or manage low-level file storage directly.
  - Does **not** alter narrative or shot structure; operates strictly within the approved `Storyboard`.

### 4. Workflow Orchestrator (`backend/app/orchestrator`)
- **Responsibilities**:
  - Own the project lifecycle state machine across all stages.
  - Enforce mandatory human `Approval` gates before advancing between major stages.
  - Dispatch agent runs and production jobs, track status transitions, and handle bounded retries and failure recovery.
  - Coordinate `ProjectVersion` creation on revisions, scene-level regeneration, and full-video regeneration.
- **Boundaries**:
  - Contains **no** prompt engineering or media-processing logic.
  - Delegates AI calls to Agents and media assembly to `Production & Media Processing`.

### 5. Model Gateway (`backend/app/model_gateway`)
- **Responsibilities**:
  - Provide typed, provider-independent interfaces across four capability domains: `llm/`, `image/`, `video/`, and `audio/`.
  - Adapt requests/responses to hosted open-weight APIs, optional local inference servers, or proprietary fallbacks.
  - Normalize provider errors (timeouts, rate limits, malformed responses, auth failures).
- **Boundaries**:
  - Stateless with respect to project workflow and approvals.
  - Contains **no** business logic about video production stages.

### 6. Input and Context Ingestion (`backend/app/ingestion`)
- **Responsibilities**:
  - Validate and normalize raw user briefs into `CreativeBrief` schemas.
  - Extract and structure reference materials (text notes, brand guidelines, uploaded reference asset metadata/URIs) into a clean context payload.
- **Boundaries**:
  - Does **not** generate creative ideas or call generative agents.
  - Rejects invalid/incomplete inputs early before pipeline execution.

### 7. Production and Media Processing (`backend/app/production`)
- **Responsibilities**:
  - Execute media post-processing and final timeline assembly (concatenating scene clips, mixing voiceover/SFX/music, transitions, encoding via FFmpeg).
  - Produce individual clip exports and final assembled video `GeneratedAsset` artifacts.
- **Boundaries**:
  - Deterministic media processing only; does **not** make creative decisions or call generative AI models.

### 8. Storage and Asset Management (`backend/app/storage`)
- **Responsibilities**:
  - Persist `Project`, `ProjectVersion`, `Approval`, `GenerationJob`, and `GeneratedAsset` records.
  - Store and retrieve versioned JSON artifacts and binary media files (clips, reference images, audio, final exports).
  - Start with a lightweight local filesystem + JSON store in early milestones, behind a clean interface that can later swap to PostgreSQL + S3-compatible storage.
- **Boundaries**:
  - Pure persistence and asset retrieval; contains **no** orchestration or AI logic.

### 9. API Layer (`backend/app/api`)
- **Responsibilities**:
  - Expose FastAPI REST endpoints for projects, briefs, stage execution, approvals, revisions, scene regeneration, and exports.
  - Enforce request/response validation via Pydantic v2 (`backend/app/schemas`) and map domain errors to clean HTTP status codes.
- **Boundaries**:
  - Thin HTTP transport layer; delegates all workflow logic to `Workflow Orchestrator` and `Input Ingestion`.

---

## Data Flow Between Components

1. **Brief Submission**: Client → `API Layer` → `Input & Context Ingestion` → produces validated `CreativeBrief` + reference context → saved by `Storage` under `Project` / initial `ProjectVersion`.
2. **Stage 1 (Creative Intelligence)**: `API Layer` triggers `Orchestrator` → invokes `Creative Intelligence Agent` → calls `Model Gateway (llm)` → returns 3 `CreativeConcept` items + 1 `CreativeDirection` → `Storage` persists versioned output → `Orchestrator` pauses at **Approval Gate 1**.
3. **Approval Gate 1**: Client submits `Approval` (`approved` or `revision_requested` with feedback) → `API Layer` → `Orchestrator` either creates a new `ProjectVersion` and re-runs Stage 1 with feedback, or unlocks Stage 2.
4. **Stage 2 (Visual Planning)**: `Orchestrator` invokes `Storyboard Director Agent` with approved `CreativeDirection` → calls `Model Gateway (llm, image)` → produces `Storyboard` + `Scene` list + Visual Bible → `Storage` persists → `Orchestrator` pauses at **Approval Gate 2**.
5. **Approval Gate 2**: Client approves or requests storyboard/scene edits → `Orchestrator` unlocks Stage 3 on approval.
6. **Stage 3 (Production & Assembly)**: `Orchestrator` invokes `Production Planner Agent` → produces `GenerationJob` plan → executes jobs via `Model Gateway (image, video, audio)` → `Storage` saves `GeneratedAsset` clips → `Production & Media Processing` assembles final video → `Orchestrator` pauses at **Final Review**.
7. **Final Review & Export**: Client approves final video (or requests `Scene`-level regeneration) → `API Layer` serves individual clips and assembled export URIs from `Storage`.
