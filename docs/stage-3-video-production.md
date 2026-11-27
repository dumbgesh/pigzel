# Stage 3 Specification — Video Production & Assembly

> **Status**: Planned specification (Milestone 4). The Production Planner agent, live video/audio providers, and FFmpeg assembly are **not yet implemented**; this branch defines the Pydantic v2 data contracts and provider/assembler interfaces.

## Purpose

The **Production Planner** translates an approved `Storyboard` into per-scene `GenerationJob` records, coordinates video and audio generation through the Model Gateway, supports independent scene-level regeneration, and hands completed `GeneratedAsset` clips to `MediaAssembler` for final export.

## Core Contracts

- **`GenerationJob`**: Tracks capability (`image | video | audio | assembly`), provider, status, attempts, and `scene_id` (for partial failure isolation and scene-level regeneration).
- **`GeneratedAsset`**: Metadata and URI for produced clips, audio tracks, and the final assembled video.
- **`VideoProvider` / `AudioProvider`**: Provider-independent `typing.Protocol` interfaces in `backend/app/model_gateway/video/base.py` and `audio/base.py`.
- **`MediaAssembler`**: Deterministic assembly interface in `backend/app/production/assembler.py` for FFmpeg-based clip concatenation and audio mixing.
