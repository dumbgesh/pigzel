# Workflow Lifecycle

> **Status**: Finalized lifecycle specification. All stage transitions, data handoffs, approvals, and regeneration semantics are defined below.

## End-to-End Pipeline

```text
User Brief
  │
  ▼
Context Ingestion ─────────────────────────────────────────┐
  │                                                        │
  ▼                                                        │
Creative Concepts (Stage 1)                                │
  │                                                        │
  ▼                                                        │
[Human Approval Gate 1] ──(Revise)──► Creative Concepts    │
  │ (Approve)                                              │
  ▼                                                        │
Storyboard (Stage 2)                                       │
  │                                                        │
  ▼                                                        │
[Human Approval Gate 2] ──(Revise)──► Storyboard           │
  │ (Approve)                                              │
  ▼                                                        │
Production Planning (Stage 3a)                             │
  │                                                        │
  ▼                                                        │
Asset Generation (Stage 3b)                                │
  │                                                        │
  ▼                                                        │
Video Assembly (Stage 3c)                                  │
  │                                                        │
  ▼                                                        │
[Final Review] ──(Regenerate Scene)──► Asset Generation    │
  │               (for target scene_id only)               │
  ├──(Full-Video Regenerate)───────────────────────────────┘
  │ (Approve)
  ▼
Export (Individual Clips + Final Video)
```

---

## Stage-by-Stage Data Handoff

| Step | Receives | Produces |
| :--- | :--- | :--- |
| **1. User Brief** | Raw user idea, format, duration, tone, mode (`simple`/`advanced`), reference uploads/URLs | Raw request payload |
| **2. Context Ingestion** | Raw request payload | Validated `CreativeBrief`, normalized reference context, initial `Project` + `ProjectVersion` (`v1`) |
| **3. Creative Concepts** | `CreativeBrief`, reference context, optional revision feedback | 3 `CreativeConcept` objects + 1 recommended `CreativeDirection` |
| **4. Human Approval (Gate 1)** | `CreativeConcept` list, `CreativeDirection` | `Approval` record (`approved` / `revision_requested`), selected `concept_id` |
| **5. Storyboard** | Approved `CreativeDirection`, `CreativeBrief`, optional revision feedback | `Storyboard` containing ordered `Scene` specs + Visual Bible + optional reference images |
| **6. Human Approval (Gate 2)** | `Storyboard`, `Scene` list, reference images | `Approval` record (`approved` / `revision_requested` / scene edits) |
| **7. Production Planning** | Approved `Storyboard` | Ordered list of `GenerationJob` specifications per `Scene` |
| **8. Asset Generation** | `GenerationJob` specs | `GeneratedAsset` records (keyframes, video clips, voiceover, SFX, music) |
| **9. Video Assembly** | Completed `GeneratedAsset` items + `Storyboard` timing | Final assembled video `GeneratedAsset` |
| **10. Final Review** | Assembled video + individual scene clips | `Approval` record (`approved` / `regenerate_scene` / `regenerate_full`) |
| **11. Export** | Approved `GeneratedAsset` URIs | Downloadable/accessible individual clips + final video |

---

## Approval Checkpoints

Human approval is mandatory at three checkpoints:
1. **Gate 1 (Post-Creative Intelligence)**: User selects/approves the `CreativeDirection` before visual planning begins.
2. **Gate 2 (Post-Visual Planning)**: User approves the `Storyboard` and `Scene` breakdown before costly video/audio generation begins.
3. **Final Review (Post-Assembly)**: User inspects the assembled video and individual clips before marking the version ready for export.

An `Approval` record captures `stage`, `project_version_id`, `decision` (`approved`, `revision_requested`, `rejected`), `feedback`, `actor`, and `timestamp`.

---

## Failure and Retry Behaviour

- **Ingestion / Schema Validation Errors**: Rejected immediately with structured validation details (no retries on invalid user input).
- **Malformed AI Output**: If an agent receives output from `ModelGateway` that fails Pydantic v2 validation, it performs up to **2 bounded retries** passing the validation error back to the LLM before marking the step failed.
- **Transient Provider Errors**: Rate limits, timeouts, and 5xx responses from external or local providers trigger bounded exponential backoff retries at the `GenerationJob` / gateway level.
- **Partial Production Failure**: Because `GenerationJob` records are tracked per `Scene`, if 1 scene fails out of 8, the 7 completed `GeneratedAsset` clips remain valid and stored. Only the failed job needs to be retried.
- **Traceability**: Every `GenerationJob` and stage output logs its `project_version_id`, provider/model identifier, attempt count, and error message on failure.

---

## Regeneration Semantics

### Scene-Level Regeneration
- Triggered when a user wants to redo a single `Scene` (e.g., new seed, adjusted prompt, or different provider) without invalidating other scenes.
- **Behavior**:
  1. Creates a new `ProjectVersion` linked to the previous version via `parent_version_id`.
  2. Reuses all unaffected `GeneratedAsset` clips from the parent version.
  3. Re-runs `GenerationJob`s only for the targeted `scene_id`.
  4. Re-runs **Video Assembly** over the updated clip set and transitions back to **Final Review**.

### Full-Video Regeneration
- Triggered when the user wants to regenerate from an earlier stage (e.g., new creative concepts from Stage 1, or a fresh storyboard from Stage 2, or re-rendering all scenes in Stage 3).
- **Behavior**:
  1. Creates a new `ProjectVersion` recording `parent_version_id` and the restart stage.
  2. Preserves the prior version intact for comparison or rollback.

---

## Version Management

- **Immutable Versions**: Once a `ProjectVersion` reaches an approval gate or completes production, its artifacts are not overwritten in place. Revisions and regenerations create a new `ProjectVersion` (`version_number` incremented monotonically per `Project`).
- **Lineage**: Every `ProjectVersion` stores `parent_version_id` so version history forms an auditable tree.
- **Active Pointer**: `Project.active_version_id` points to the current working version, while earlier versions remain readable for comparison or rollback.
