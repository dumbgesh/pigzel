# Data Contracts

> **Status**: Core domain entity specifications. Designed for direct implementation in `backend/app/schemas/` using Pydantic v2.

## Entity Relationship Overview

```text
Project (1) ──< ProjectVersion (N)
                    │
                    ├── (1) CreativeBrief
                    ├── (N) CreativeConcept
                    ├── (0..1) CreativeDirection
                    ├── (0..1) Storyboard ──< Scene (N)
                    │                           │
                    │                           └──< GenerationJob (N) ──> GeneratedAsset (0..1)
                    └──< Approval (N)
```

---

## 1. `Project`
Top-level container for a user's video production initiative.

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `str` (UUID) | Unique project identifier |
| `title` | `str` | Human-readable project title |
| `mode` | `Literal["simple", "advanced"]` | Workflow UI/control mode |
| `active_version_id` | `str` | Currently active `ProjectVersion.id` |
| `created_at` | `datetime` | UTC creation timestamp |
| `updated_at` | `datetime` | UTC last update timestamp |

## 2. `ProjectVersion`
Immutable snapshot of pipeline state, artifacts, and stage progress for a project iteration.

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `str` (UUID) | Unique version identifier |
| `project_id` | `str` | Parent `Project.id` |
| `version_number` | `int` | Monotonic per-project version (`1, 2, 3...`) |
| `parent_version_id` | `str \| None` | Previous `ProjectVersion.id` if branched/revised |
| `current_stage` | `enum` | `ingestion`, `creative`, `approval_1`, `storyboard`, `approval_2`, `production`, `assembly`, `final_review`, `completed`, `failed` |
| `brief` | `CreativeBrief` | Normalized brief for this version |
| `concepts` | `list[CreativeConcept]` | Generated concepts (3 when Stage 1 completes) |
| `direction` | `CreativeDirection \| None` | Approved/recommended creative direction |
| `storyboard` | `Storyboard \| None` | Generated storyboard |
| `created_at` | `datetime` | UTC creation timestamp |

## 3. `CreativeBrief`
Validated user input and ingested reference context.

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `str` (UUID) | Brief identifier |
| `idea` | `str` | Core user idea or prompt (non-empty) |
| `format` | `enum` | `ad`, `social`, `promo`, `explainer`, `short_film`, `brand_film`, `custom` |
| `target_duration_seconds` | `int \| None` | Desired duration in seconds (`> 0`) |
| `aspect_ratio` | `str` | e.g. `"16:9"`, `"9:16"`, `"1:1"` (default `"16:9"`) |
| `target_audience` | `str \| None` | Intended audience description |
| `tone` | `str \| None` | Desired tone/mood (e.g., `"energetic"`, `"cinematic"`) |
| `constraints` | `list[str]` | Explicit do/don't rules or brand constraints |
| `reference_notes` | `list[str]` | Extracted text notes/context from references |
| `reference_asset_uris` | `list[str]` | URIs to uploaded reference files (images, docs) |

## 4. `CreativeConcept`
One of three distinct creative proposals generated in Stage 1.

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `str` | Concept identifier within the proposal (e.g., `"concept_1"`) |
| `title` | `str` | Short, memorable concept title |
| `premise` | `str` | Core hook and angle |
| `narrative_arc` | `str` | Beginning, middle, end summary |
| `visual_style` | `str` | High-level visual aesthetic |
| `audio_style` | `str` | High-level voiceover/music/SFX feel |
| `rationale` | `str` | Why this concept fits the `CreativeBrief` |

## 5. `CreativeDirection`
The recommended (and upon approval, selected) production blueprint from Stage 1.

| Field | Type | Description |
| :--- | :--- | :--- |
| `selected_concept_id` | `str` | Matches one `CreativeConcept.id` |
| `narrative_summary` | `str` | Detailed story/messaging flow |
| `pacing_guidance` | `str` | Pacing and rhythm instructions |
| `visual_guidelines` | `str` | Color, framing, and aesthetic direction |
| `audio_guidelines` | `str` | Voiceover, music, and sound direction |
| `production_instructions` | `list[str]` | Actionable instructions for Stage 2 & Stage 3 |

## 6. `Storyboard`
Structured visual plan produced in Stage 2.

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `str` (UUID) | Storyboard identifier |
| `project_version_id` | `str` | Owning `ProjectVersion.id` |
| `visual_bible` | `dict` / `VisualBible` | Canonical character, environment, palette, and style rules |
| `scenes` | `list[Scene]` | Ordered sequence of scenes (`>= 1`) |
| `total_estimated_duration_seconds` | `float` | Sum of scene durations |

## 7. `Scene`
An individual, independently addressable unit within a `Storyboard`.

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `str` (UUID) | Unique scene identifier |
| `order` | `int` | 1-based sequence index |
| `duration_seconds` | `float` | Target clip duration (`> 0`) |
| `description` | `str` | Narrative action occurring in the scene |
| `shot_type` | `str` | e.g., `"wide"`, `"medium"`, `"close-up"` |
| `camera_movement` | `str` | e.g., `"static"`, `"slow pan"`, `"dolly in"` |
| `lighting` | `str` | Lighting setup and mood |
| `environment` | `str` | Setting/location description |
| `visual_prompt` | `str` | Generation-ready visual prompt |
| `audio_cue` | `str \| None` | Dialogue, voiceover line, SFX, or music cue |
| `reference_asset_ids` | `list[str]` | Linked keyframe or visual reference `GeneratedAsset.id`s |

## 8. `GenerationJob`
A single unit of AI media generation work in Stage 3 (or Stage 2 reference generation).

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `str` (UUID) | Unique job identifier |
| `project_version_id` | `str` | Owning `ProjectVersion.id` |
| `scene_id` | `str \| None` | Target `Scene.id` (`None` for project-wide assembly/music) |
| `capability` | `Literal["image", "video", "audio", "assembly"]` | Gateway capability or assembly step |
| `provider` | `str` | Provider identifier used |
| `status` | `Literal["pending", "running", "succeeded", "failed", "cancelled"]` | Execution state |
| `attempts` | `int` | Number of execution attempts |
| `input_params` | `dict` | Serialized prompt/parameters (for reproducibility) |
| `output_asset_id` | `str \| None` | Resulting `GeneratedAsset.id` on success |
| `error_message` | `str \| None` | Normalized error detail on failure |
| `created_at` | `datetime` | UTC creation timestamp |
| `updated_at` | `datetime` | UTC last update timestamp |

## 9. `GeneratedAsset`
Metadata pointing to a stored media artifact produced by a `GenerationJob`.

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `str` (UUID) | Unique asset identifier |
| `project_version_id` | `str` | Originating `ProjectVersion.id` |
| `scene_id` | `str \| None` | Associated `Scene.id`, if scene-specific |
| `asset_type` | `Literal["reference_image", "video_clip", "audio_track", "assembled_video"]` | Artifact category |
| `uri` | `str` | Storage URI or relative path |
| `mime_type` | `str` | e.g., `"video/mp4"`, `"image/png"`, `"audio/wav"` |
| `duration_seconds` | `float \| None` | Media duration for video/audio |
| `created_at` | `datetime` | UTC creation timestamp |

## 10. `Approval`
Explicit human-in-the-loop decision at a workflow gate.

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `str` (UUID) | Unique approval identifier |
| `project_version_id` | `str` | Reviewed `ProjectVersion.id` |
| `gate` | `Literal["creative_direction", "storyboard", "final_review"]` | Checkpoint name |
| `decision` | `Literal["approved", "revision_requested", "rejected"]` | Human decision |
| `feedback` | `str \| None` | Optional revision instructions or notes |
| `selected_concept_id` | `str \| None` | Optional concept override at Gate 1 |
| `created_at` | `datetime` | UTC timestamp |
