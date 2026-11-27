# Stage 2 Specification — Visual Planning

> **Status**: Planned specification (Milestone 3). The Storyboard Director agent and live image generation are **not yet implemented**; this branch defines the Pydantic v2 data contracts and provider interfaces.

## Purpose

The **Storyboard Director** converts an approved `CreativeDirection` (from Stage 1) into a structured `Storyboard` composed of ordered `Scene` specifications and a consistent `VisualBible`.

## Core Contracts

- **`VisualBible`**: Canonical character descriptions, environment notes, color palette, and style rules shared across all scenes.
- **`Scene`**: Independently addressable unit specifying `order`, `duration_seconds`, `shot_type`, `camera_movement`, `lighting`, `environment`, `visual_prompt`, and `audio_cue`.
- **`Storyboard`**: Ordered list of `Scene` items with 1-based sequential ordering and `total_estimated_duration_seconds`.
- **`ImageProvider`**: Provider-independent `typing.Protocol` in `backend/app/model_gateway/image/base.py` for generating keyframe/reference images.
