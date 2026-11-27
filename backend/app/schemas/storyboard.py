"""Pydantic v2 contract schemas for Stage 2 — Visual Planning (Storyboard & Visual Bible)."""

from pydantic import BaseModel, Field, field_validator, model_validator


def _strip_required(value: str, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty or whitespace.")
    return cleaned


class VisualBible(BaseModel):
    """Canonical visual continuity rules shared across all storyboard scenes."""

    style_summary: str = Field(..., min_length=5, max_length=2000)
    color_palette: list[str] = Field(default_factory=list)
    character_notes: dict[str, str] = Field(default_factory=dict)
    environment_notes: dict[str, str] = Field(default_factory=dict)
    continuity_rules: list[str] = Field(default_factory=list)

    @field_validator("style_summary")
    @classmethod
    def validate_style_summary(cls, value: str, info) -> str:
        return _strip_required(value, info.field_name)


class Scene(BaseModel):
    """An individual, independently addressable scene within a Storyboard."""

    id: str = Field(..., min_length=1, max_length=64)
    order: int = Field(..., ge=1)
    duration_seconds: float = Field(..., gt=0, le=300)
    description: str = Field(..., min_length=5, max_length=2000)
    shot_type: str = Field(..., min_length=2, max_length=100)
    camera_movement: str = Field(..., min_length=2, max_length=100)
    lighting: str = Field(..., min_length=2, max_length=300)
    environment: str = Field(..., min_length=2, max_length=500)
    visual_prompt: str = Field(..., min_length=5, max_length=3000)
    audio_cue: str | None = Field(default=None, max_length=1000)
    reference_asset_ids: list[str] = Field(default_factory=list)

    @field_validator(
        "id",
        "description",
        "shot_type",
        "camera_movement",
        "lighting",
        "environment",
        "visual_prompt",
    )
    @classmethod
    def validate_required_fields(cls, value: str, info) -> str:
        return _strip_required(value, info.field_name)


class Storyboard(BaseModel):
    """Ordered visual plan produced in Stage 2."""

    id: str = Field(..., min_length=1, max_length=64)
    visual_bible: VisualBible
    scenes: list[Scene] = Field(..., min_length=1)

    @property
    def total_estimated_duration_seconds(self) -> float:
        """Return the sum of all scene durations in seconds."""
        return round(sum(scene.duration_seconds for scene in self.scenes), 2)

    @model_validator(mode="after")
    def validate_scene_ordering_and_ids(self) -> "Storyboard":
        scene_ids = [s.id for s in self.scenes]
        if len(set(scene_ids)) != len(scene_ids):
            raise ValueError("All scenes in a Storyboard must have unique IDs.")

        orders = [s.order for s in self.scenes]
        expected_orders = list(range(1, len(self.scenes) + 1))
        if orders != expected_orders:
            raise ValueError(f"Scene order must be sequential 1..{len(self.scenes)}, got {orders}.")
        return self
