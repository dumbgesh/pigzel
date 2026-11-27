# Product Requirements

> **Status**: Confirmed baseline requirements. Features listed here define the target product scope and are not yet implemented.

## Target Users

- **Creators**: Solo video creators needing fast concept-to-video workflows.
- **Agencies**: Creative and marketing teams producing client campaigns with review gates.
- **Production Studios**: Teams requiring granular scene control, visual consistency, and reusable clips.
- **Social Media Teams**: High-velocity short-form content production across formats.
- **Developers**: Engineers extending or self-hosting a modular, open-source AI video pipeline.

## Supported Video Formats

Pigzel must support both **short-form** and **long-form** video production, including:

- Advertisements
- Social media content
- Promotional videos
- Explainer videos
- Short films
- Brand films
- Other custom creative video formats

## User Modes

### Simple Mode
- Guided, minimal-friction workflow from idea to finished video.
- Sensible defaults for pacing, visual style, and provider selection.
- Clear stage approval checkpoints without exposing low-level production parameters.

### Advanced Mode
- Full visibility and editability of creative directions, storyboards, and the visual bible.
- Granular control over shot types, camera movements, lighting, environments, and prompts.
- Independent scene-level regeneration and provider/model selection per capability.

## Core Functional Requirements

1. **Complete Idea-to-Video Production**
   - Accept natural-language ideas, structured instructions, and reference materials (images, brand notes, style guides).
   - Execute the three-stage pipeline (Creative Intelligence → Visual Planning → Video Production).

2. **Human-in-the-Loop Approvals**
   - Require explicit human approval between major stages before advancing.
   - Support revision requests with feedback at each approval gate.

3. **Versioned Creative Outputs**
   - Preserve versions of creative concepts, storyboards, and generated clips so users can compare or roll back.

4. **Scene-Level & Full-Video Regeneration**
   - Allow regenerating a single scene (or specific asset within a scene) without invalidating unaffected scenes.
   - Support full-pipeline or full-video regeneration when creative direction changes.

5. **Flexible Exports**
   - Export individual generated scene clips.
   - Export the fully assembled final video.

6. **Traceability & Failure Recovery**
   - Record which inputs, schemas, and model providers produced each artifact.
   - Recover gracefully from transient provider failures at the job/scene level.
