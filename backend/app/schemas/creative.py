"""Pydantic v2 schemas for Stage 1 — Creative Intelligence."""

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, Field, field_validator, model_validator


def _strip_required(value: str, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty or whitespace.")
    return cleaned


def _strip_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _clean_string_list(values: list[str]) -> list[str]:
    return [item.strip() for item in values if item and item.strip()]


class VideoFormat(StrEnum):
    """Supported video formats across Pigzel."""

    AD = "ad"
    SOCIAL = "social"
    PROMO = "promo"
    EXPLAINER = "explainer"
    SHORT_FILM = "short_film"
    BRAND_FILM = "brand_film"
    CUSTOM = "custom"


class CreativeBrief(BaseModel):
    """Structured user input brief for Stage 1 Creative Intelligence."""

    project_name: str | None = Field(default=None, max_length=200)
    video_type: VideoFormat = Field(default=VideoFormat.CUSTOM)
    idea: str = Field(..., min_length=5, max_length=4000)
    objective: str | None = Field(default=None, max_length=1000)
    target_audience: str | None = Field(default=None, max_length=500)
    platform: str | None = Field(default=None, max_length=200)
    desired_duration_seconds: int | None = Field(default=None, gt=0, le=1800)
    aspect_ratio: str = Field(default="16:9", min_length=3, max_length=20)
    tone_and_style: str | None = Field(default=None, max_length=500)
    language: str = Field(default="en", min_length=2, max_length=20)
    brand_or_product_info: str | None = Field(default=None, max_length=2000)
    constraints: list[str] = Field(default_factory=list)
    reference_materials: list[str] = Field(default_factory=list)

    @field_validator("idea", "aspect_ratio", "language")
    @classmethod
    def validate_required_strings(cls, value: str, info) -> str:
        return _strip_required(value, info.field_name)

    @field_validator(
        "project_name",
        "objective",
        "target_audience",
        "platform",
        "tone_and_style",
        "brand_or_product_info",
    )
    @classmethod
    def validate_optional_strings(cls, value: str | None) -> str | None:
        return _strip_optional(value)

    @field_validator("constraints", "reference_materials")
    @classmethod
    def validate_string_lists(cls, value: list[str]) -> list[str]:
        return _clean_string_list(value)


class CreativeConcept(BaseModel):
    """A single distinct creative concept generated in Stage 1."""

    id: str = Field(..., min_length=1, max_length=64)
    title: str = Field(..., min_length=2, max_length=200)
    core_idea: str = Field(..., min_length=5, max_length=2000)
    creative_approach: str = Field(..., min_length=5, max_length=2000)
    narrative_summary: str = Field(..., min_length=5, max_length=3000)
    target_audience: str = Field(..., min_length=2, max_length=500)
    tone: str = Field(..., min_length=2, max_length=200)
    visual_direction: str = Field(..., min_length=5, max_length=2000)
    key_message: str = Field(..., min_length=2, max_length=1000)
    suggested_duration_seconds: int = Field(..., gt=0, le=1800)
    reasoning: str = Field(..., min_length=5, max_length=2000)

    @field_validator(
        "id",
        "title",
        "core_idea",
        "creative_approach",
        "narrative_summary",
        "target_audience",
        "tone",
        "visual_direction",
        "key_message",
        "reasoning",
    )
    @classmethod
    def validate_non_empty(cls, value: str, info) -> str:
        return _strip_required(value, info.field_name)


class CreativeDirection(BaseModel):
    """Recommended production direction derived from the chosen concept."""

    selected_concept_id: str = Field(..., min_length=1, max_length=64)
    narrative_summary: str = Field(..., min_length=5, max_length=3000)
    pacing_guidance: str = Field(..., min_length=5, max_length=1500)
    visual_guidelines: str = Field(..., min_length=5, max_length=2000)
    audio_guidelines: str = Field(..., min_length=5, max_length=2000)
    production_instructions: list[str] = Field(..., min_length=1)

    @field_validator(
        "selected_concept_id",
        "narrative_summary",
        "pacing_guidance",
        "visual_guidelines",
        "audio_guidelines",
    )
    @classmethod
    def validate_non_empty(cls, value: str, info) -> str:
        return _strip_required(value, info.field_name)

    @field_validator("production_instructions")
    @classmethod
    def validate_instructions(cls, value: list[str]) -> list[str]:
        cleaned = _clean_string_list(value)
        if not cleaned:
            raise ValueError("production_instructions must contain at least one non-empty item.")
        return cleaned


class CreativeIntelligencePayload(BaseModel):
    """Structured payload expected from the LLM before gateway metadata is attached."""

    concepts: Annotated[list[CreativeConcept], Field(min_length=3, max_length=3)]
    recommended_concept_id: str = Field(..., min_length=1, max_length=64)
    recommendation_explanation: str = Field(..., min_length=5, max_length=2000)
    direction: CreativeDirection

    @field_validator("recommended_concept_id", "recommendation_explanation")
    @classmethod
    def validate_non_empty(cls, value: str, info) -> str:
        return _strip_required(value, info.field_name)

    @model_validator(mode="after")
    def validate_concept_uniqueness_and_recommendation(self) -> "CreativeIntelligencePayload":
        concept_ids = [c.id for c in self.concepts]
        if len(set(concept_ids)) != 3:
            raise ValueError("All three concepts must have unique IDs.")

        titles = [c.title.lower() for c in self.concepts]
        if len(set(titles)) != 3:
            raise ValueError("All three concepts must have distinct titles.")

        if self.recommended_concept_id not in concept_ids:
            raise ValueError(
                f"recommended_concept_id '{self.recommended_concept_id}' "
                f"must match one of {concept_ids}."
            )

        if self.direction.selected_concept_id != self.recommended_concept_id:
            raise ValueError(
                "direction.selected_concept_id must match recommended_concept_id."
            )

        return self


class CreativeIntelligenceResult(CreativeIntelligencePayload):
    """Final validated Stage 1 output including model gateway provenance."""

    provider_name: str
    model_name: str
    is_mock: bool = False
